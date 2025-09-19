import './App.css'

import { generateAPCAPalette } from './color'

function Palette({ name, hex }: {name: string, hex: string}) {
  const palette = generateAPCAPalette({
    base: hex
  });
  return (
    <div className='wrapper'>
      <h1>{name} - {palette.length}</h1>
      {palette.map((row: any) => {
        return (
          <div className='card'>
            <h2>{row.token}</h2>
            <button onClick={() => navigator.clipboard.writeText(row.hex)}>Copy</button>
            <div
              className='cardColor'
              key={row.hex}
              style={{ backgroundColor: row.hex }}
            />

          </div>
        )
      })}
    </div>
  )
}

function App() {
  return (
    <div >
      <Palette name="purple" hex="#955AAA" />
      <Palette name="green" hex="#317E85" />
      <Palette name="blue" hex="#706DA8" />
      <Palette name="gray" hex="#6B7482" />
      <Palette name="neutral" hex="#B0B0B0" />
    </div>
  )
}

export default App
