import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
let inPath = args[1]
let outPath = args[2]
let scale = CGFloat(Double(args[3]) ?? 3.0)
guard let doc = PDFDocument(url: URL(fileURLWithPath: inPath)), let page = doc.page(at: 0) else { exit(1) }
let bounds = page.bounds(for: .mediaBox)
let w = Int(bounds.width * scale), h = Int(bounds.height * scale)
let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0, space: cs, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { exit(1) }
ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
ctx.scaleBy(x: scale, y: scale)
page.draw(with: .mediaBox, to: ctx)
guard let img = ctx.makeImage() else { exit(1) }
let rep = NSBitmapImageRep(cgImage: img)
guard let data = rep.representation(using: .png, properties: [:]) else { exit(1) }
try! data.write(to: URL(fileURLWithPath: outPath))
print("wrote \(outPath) \(w)x\(h)")
