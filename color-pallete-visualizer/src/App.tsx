import './App.css'

import { generateAPCAPalette } from './color'

function Palette({ name, hex }: {name: string, hex: string}) {
  const palette = generateAPCAPalette({
    base: hex
  });
  return (
    <details>
      <summary>{name} <span style={{backgroundColor: hex}}>(base {hex})</span> - {palette.length} colors</summary>
      <div className='wrapper'>
        {palette.map((row: any) => {
          return (
            <div className='card'>
              <h2>{row.token}</h2>
              
              <button onClick={() => navigator.clipboard.writeText(row.hex)}>Copy hex</button>
              <div
                className='cardColor'
                key={row.hex}
                style={{ backgroundColor: row.hex, border: "1px black solid" }}
              >
                <p style={{color: (row.APCA_target > 0 ? 'white' : 'black')}}>{row.hex}</p>
              </div>

            </div>
          )
        })}
      </div>
    </details>
  )
}

function App() {
  return (
    <div>
      <Palette name="purple" hex="#955AAA" />
      <Palette name="green" hex="#317E85" />
      <Palette name="blue" hex="#706DA8" />
      <Palette name="gray" hex="#6B7482" />

      <Palette name="purple" hex="#7A3093" />
      <Palette name="green" hex="#195D63" />
      <Palette name="blue" hex="#4C4698" />
      <Palette name="gray" hex="#4C576A" />
    </div>
  )
}

export default App
