// Iguala el color y el brillo de varias fotos recortadas (PNG con transparencia) de la misma ave,
// para que se vean como de una misma sesión.
// Uso: igualar <carpeta_salida> <foto1.png> <foto2.png> ...
// Calcula el color promedio de la parte visible de cada foto (sin el fondo transparente),
// toma el promedio del grupo como meta y corrige cada foto hacia esa meta de forma moderada.
import Foundation
import CoreImage

func fail(_ m: String) -> Never { FileHandle.standardError.write((m + "\n").data(using: .utf8)!); exit(1) }

let args = CommandLine.arguments
guard args.count >= 3 else { fail("uso: igualar <carpeta_salida> <foto1.png> ...") }
let outDir = URL(fileURLWithPath: args[1], isDirectory: true)
let inputs = args.dropFirst(2).map { URL(fileURLWithPath: $0) }
let ctx = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.sRGB)!])
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!

// Promedio (premultiplicado) y luego dividido por alfa = color medio de la parte visible
func promedio(_ img: CIImage) -> (r: Double, g: Double, b: Double) {
    let f = CIFilter(name: "CIAreaAverage", parameters: [kCIInputImageKey: img, kCIInputExtentKey: CIVector(cgRect: img.extent)])!
    var px = [Float](repeating: 0, count: 4)
    ctx.render(f.outputImage!, toBitmap: &px, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBAf, colorSpace: srgb)
    let a = max(Double(px[3]), 1e-4)
    return (Double(px[0]) / a, Double(px[1]) / a, Double(px[2]) / a)
}

var imgs: [CIImage] = []
var medias: [(r: Double, g: Double, b: Double)] = []
for u in inputs {
    guard let im = CIImage(contentsOf: u) else { fail("no se pudo abrir \(u.path)") }
    imgs.append(im)
    medias.append(promedio(im))
}
let n = Double(medias.count)
let meta = (r: medias.map { $0.r }.reduce(0, +) / n, g: medias.map { $0.g }.reduce(0, +) / n, b: medias.map { $0.b }.reduce(0, +) / n)
let lumMeta = 0.2126 * meta.r + 0.7152 * meta.g + 0.0722 * meta.b

for (i, im) in imgs.enumerated() {
    let m = medias[i]
    // Solo se iguala el brillo, con la misma ganancia en los tres canales: así no cambia el tono del ave.
    // (Igualar cada canal por separado falla cuando una foto es de frente y otra de espalda.)
    let lum = 0.2126 * m.r + 0.7152 * m.g + 0.0722 * m.b
    let ganancia = CGFloat(min(1.2, max(0.86, 1 + 0.6 * (lumMeta / max(lum, 1e-4) - 1))))
    let gr = ganancia, gg = ganancia, gb = ganancia
    var out = im.applyingFilter("CIColorMatrix", parameters: [
        "inputRVector": CIVector(x: gr, y: 0, z: 0, w: 0),
        "inputGVector": CIVector(x: 0, y: gg, z: 0, w: 0),
        "inputBVector": CIVector(x: 0, y: 0, z: gb, w: 0),
    ])
    // Contraste y saturación parejos y un poco más de vida, como fotos editadas juntas
    out = out.applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 1.06, kCIInputContrastKey: 1.04, kCIInputBrightnessKey: 0.0])
    let nombre = inputs[i].deletingPathExtension().lastPathComponent + "-ig.png"
    do {
        try ctx.writePNGRepresentation(of: out, to: outDir.appendingPathComponent(nombre), format: .RGBA8, colorSpace: srgb)
    } catch { fail("no se pudo guardar \(nombre): \(error)") }
    print(String(format: "%@  ganancias R %.2f G %.2f B %.2f  (brillo %.2f -> meta %.2f)", nombre, gr, gg, gb, lum, lumMeta))
}
