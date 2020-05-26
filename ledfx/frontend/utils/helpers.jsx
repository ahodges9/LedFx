export const includeKeyInObject = (key, object) => ({ id: key, ...object})

export const mapIncludeKey = (scenes) => {
    const keys = Object.keys(scenes)
    return keys.map((k) => (includeKeyInObject(k, scenes[k])))
}

// convert r,g,b values to css hex format, eg. #112233
export const RGBToHex = (r, g, b) => {
    r = Math.round(r).toString(16);
    g = Math.round(g).toString(16);
    b = Math.round(b).toString(16);

    if (r.length == 1) r = "0" + r;
    if (g.length == 1) g = "0" + g;
    if (b.length == 1) b = "0" + b;

    return "#" + r + g + b;
  };