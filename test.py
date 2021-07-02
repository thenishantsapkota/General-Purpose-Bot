import asyncio

from carbonnow import Carbon

code = """
const pluckDeep = key => obj => key.split('.').reduce((accum, key) => accum[key], obj)
const compose = (...fns) => res => fns.reduce((accum, next) => next(accum), res)
const unfold = (f, seed) => {
  const go = (f, seed, acc) => {
    const res = f(seed)
    return res ? go(f, res[1], acc.concat([res[0]])) : acc
  }
  return go(f, seed, [])
}
"""


async def main():
    carbon = Carbon(
        code=code,  # Required: Code
        background='#4a90e6',  # Optional: Hex-Color for Background
        drop_shadow=True,  # Optional: Drop Shadow on div Box
        drop_shadow_blur='68px',  # Optional: Drop Shadow Blur on div Box
        drop_shadow_offset='20px',  # Optional: Drop Shadow Offset on div Box
        export_size='4x',  # Optional: Export Size (1x, 2x, 4x)
        font_size='14px',  # Optional: Font size
        font_family='Fira Code',  # Optional: support FontFamily on carbon.now.sh
        first_line_number=1,  # Optional: Starting Line Numbers if Line Numbers Exist
        language='javascript',  # Optional: Programming Language of Choice
        line_height='133%',  # Optional: Line Height
        line_numbers=False,  # Optional: Line Numbers
        padding_horizontal='56px',  # Optional: Horizontal Padding
        padding_vertical='56px',  # Optional: Vertical Padding
        theme='Material',  # Optional: Carbon Theme
        watermark=False,  # Optional: Carbon Watermark
        width_adjustment=True,  # Optional: Width Adjustment
        window_controls=False,  # Optional: Window Controls
        window_theme='Material',  # Optional: Window Theme
    )
    print(await carbon.save('carbon_photo'))  # Print Path of the file


if __name__ == '__main__':
    asyncio.run(main())