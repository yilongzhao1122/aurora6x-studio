// Record real AuroraView drawing logic with deterministic sample data.
// This harness is not the Garmin VM; the Python check uses actual glyph pixels.
const {render}=require('./preview_from_source.cjs');
const cases=[['default',render()],['imports',render({A1:0,A3:0,A4:2,C1:0,C2:0,C3:12,C4:3,C5:14},{condition:0})]];
for(const slot of ['C2','C3','C4','C5'])
  for(let field=0;field<29;field++)
    for(const [kind,extra] of [['normal',{}],['large',{large:true}],['missing',{missing:true}]])
      cases.push([`${slot}-${field}-${kind}`,render({[slot]:field},extra)]);
for(let condition=0;condition<54;condition++)cases.push([`weather-${condition}`,render({A1:0,A3:0},{condition})]);
for(const [slot,count] of [['A0',7],['A1',4],['A2',5],['A3',4],['A4',3],['C0',4],['C1',4],['C6',7]])
  for(let value=0;value<count;value++)cases.push([`${slot}-${value}`,render({[slot]:value})]);
for(const color of [0xFFFFFF,0x55FFFF,0xFF5500])cases.push([`color-${color}`,render({DataColor:color})]);
cases.push(['sleep',render({}, {sleep:true})],['low-memory',render({}, {lowMemory:true})]);
for(const [label,scene] of cases)process.stdout.write(JSON.stringify({label,...scene})+'\n');
