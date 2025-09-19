import './App.css'



import purplePalette from '../../apca_generator/purpleish2.json' with { type: 'json' }
import { generateAPCAPalette } from './color'

const paletteSorted = purplePalette.sort((a, b) => {
  return a.APCA_target - b.APCA_target
})

const purple = generateAPCAPalette({
  base: "#955AAA"
});
const green = generateAPCAPalette({
  base: "#317E85"
});
const blue = generateAPCAPalette({
  base: "#706DA8"
});


function Palette({ name, hex }) {
  const palette = generateAPCAPalette({
    base: hex
  });
  return (
    <div className='wrapper'>
      <h1>{name} - {palette.length}</h1>
      {palette.map((row) => {
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
