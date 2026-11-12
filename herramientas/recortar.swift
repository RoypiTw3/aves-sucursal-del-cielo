// Quita el fondo de una foto con Vision de macOS y la guarda como PNG transparente,
// recortada al contorno del sujeto.
// Uso: recortar <entrada.jpg> <salida.png> [mayor|todas]
//   mayor (por defecto): deja solo el sujeto más grande (el ave).
//   todas: deja todo lo que Vision considere primer plano (por ejemplo, ave + rama).
import Foundation
import Vision
import CoreImage

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 3 else { fail("uso: recortar <entrada> <salida.png> [mayor|todas]") }
let input = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2])
let modo = args.count > 3 ? args[3] : "mayor"

guard let image = CIImage(contentsOf: input, options: [.applyOrientationProperty: true]) else {
    fail("no se pudo abrir \(input.path)")
}
let handler = VNImageRequestHandler(ciImage: image, options: [:])
let request = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([request]) } catch { fail("Vision falló: \(error)") }
guard let obs = request.results?.first, !obs.allInstances.isEmpty else { fail("no se encontró sujeto") }

var instances = obs.allInstances
if modo == "mayor" && instances.count > 1 {
    let mask = obs.instanceMask
    CVPixelBufferLockBaseAddress(mask, .readOnly)
    let w = CVPixelBufferGetWidth(mask), h = CVPixelBufferGetHeight(mask), bpr = CVPixelBufferGetBytesPerRow(mask)
    let base = CVPixelBufferGetBaseAddress(mask)!.assumingMemoryBound(to: UInt8.self)
    var counts = [Int](repeating: 0, count: 256)
    for y in 0..<h {
        let row = base + y * bpr
        for x in 0..<w { counts[Int(row[x])] += 1 }
    }
    CVPixelBufferUnlockBaseAddress(mask, .readOnly)
    let best = instances.max(by: { counts[$0] < counts[$1] })!
    instances = IndexSet(integer: best)
}

do {
    // Máscara al tamaño de la foto
    let maskBuf = try obs.generateScaledMaskForImage(forInstances: instances, from: handler)
    let ext = image.extent
    // Caja del sujeto (filas de arriba hacia abajo en el buffer)
    CVPixelBufferLockBaseAddress(maskBuf, .readOnly)
    let mw = CVPixelBufferGetWidth(maskBuf), mh = CVPixelBufferGetHeight(maskBuf), mbpr = CVPixelBufferGetBytesPerRow(maskBuf)
    let mbase = CVPixelBufferGetBaseAddress(maskBuf)!
    var minX = mw, minY = mh, maxX = -1, maxY = -1
    for y in 0..<mh {
        let row = (mbase + y * mbpr).assumingMemoryBound(to: Float32.self)
        for x in 0..<mw where row[x] > 0.5 {
            if x < minX { minX = x }; if x > maxX { maxX = x }
            if y < minY { minY = y }; if y > maxY { maxY = y }
        }
    }
    CVPixelBufferUnlockBaseAddress(maskBuf, .readOnly)
    guard maxX >= minX, maxY >= minY else { fail("máscara vacía") }

    // Encoger el borde para quitar el halo del fondo y suavizarlo un poco
    let radio = max(1.0, Double(max(mw, mh)) / 1100.0)
    var mask = CIImage(cvPixelBuffer: maskBuf)
    mask = mask.applyingFilter("CIMorphologyMinimum", parameters: ["inputRadius": radio]).cropped(to: ext)
    mask = mask.applyingGaussianBlur(sigma: radio * 0.45).cropped(to: ext)
    let clear = CIImage(color: .clear).cropped(to: ext)
    let blended = image.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: clear, kCIInputMaskImageKey: mask])

    // CoreImage cuenta Y desde abajo
    let m = 4
    let box = CGRect(x: max(0, minX - m), y: max(0, mh - 1 - maxY - m),
                     width: min(mw, maxX + m + 1) - max(0, minX - m),
                     height: min(mh, (mh - 1 - minY) + m + 1) - max(0, mh - 1 - maxY - m))
    let out = blended.cropped(to: box).transformed(by: CGAffineTransform(translationX: -box.minX, y: -box.minY))
    try CIContext().writePNGRepresentation(of: out, to: output, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
    print("ok \(Int(out.extent.width))x\(Int(out.extent.height)) sujetos=\(obs.allInstances.count)")
} catch {
    fail("no se pudo guardar: \(error)")
}
