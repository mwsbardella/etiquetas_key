from PIL import Image, ImageDraw


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo arredondado — azul-teal
    bg = (20, 120, 140)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=bg)

    # Corpo da etiqueta (branco)
    m = size // 7
    lw = size - 2 * m
    lh = int(lw * 1.25)
    lx, ly = m, (size - lh) // 2
    lr = max(2, size // 14)
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=lr, fill="white")

    # Furo no topo da etiqueta
    hr = max(1, size // 16)
    hcx = lx + lw // 2
    hcy = ly + size // 11
    draw.ellipse([hcx - hr, hcy - hr, hcx + hr, hcy + hr], fill=bg)

    # Linhas de texto (placeholder)
    line_color = "#CCCCCC"
    lh_line = max(1, size // 28)
    ll = lx + size // 10
    lr2 = lx + lw - size // 10
    text_top = ly + int(lh * 0.28)
    gap = lh_line + max(2, size // 20)
    for i, frac in enumerate([1.0, 0.6]):
        y = text_top + i * gap
        draw.rectangle([ll, y, int(ll + (lr2 - ll) * frac), y + lh_line], fill=line_color)

    # Código de barras
    bar_top = ly + int(lh * 0.56)
    bar_bot = ly + int(lh * 0.84)
    bl = ll
    br = lr2
    bw = br - bl
    pattern = [2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 1, 1]
    total_units = sum(pattern)
    unit = bw / total_units
    x = bl
    for i, w in enumerate(pattern):
        x1 = int(x)
        x2 = max(x1, int(x + w * unit) - 1)
        if i % 2 == 0 and x2 > x1:  # barras pares = preto
            draw.rectangle([x1, bar_top, x2, bar_bot], fill="#1A1A1A")
        x += w * unit

    return img


if __name__ == "__main__":
    # Gera cada tamanho nativo e salva como ICO multi-resolução
    sizes = [256, 128, 64, 48, 32, 24, 16]
    images = [draw_icon(s) for s in sizes]

    # Converte cada imagem para RGBA explicitamente
    images = [img.convert("RGBA") for img in images]

    # O PIL salva ICO multi-size via 'sizes' passando a imagem maior
    # e deixando ele redimensionar — mas queremos nossas versões nativas.
    # Usamos save com append_images a partir da maior imagem.
    images[0].save(
        "icone.ico",
        format="ICO",
        append_images=images[1:],
    )

    import os
    kb = os.path.getsize("icone.ico") / 1024
    print(f"icone.ico gerado com sucesso ({kb:.1f} KB, {len(sizes)} tamanhos)")
