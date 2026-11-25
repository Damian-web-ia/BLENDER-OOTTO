/* Recuerdos añadidos solos por las tareas de cada noche (copiados de la base de datos de Claude).
   Se añaden a la lista R antes de construir el cerebro. */
[
["2026-11-25-cerebro-automatico", "El cerebro aprende solo", "decision", "11-25", "Damián no quiere añadir recuerdos a mano: cada noche Claude añade automáticamente los recuerdos del día.", ["o_cerebro"]],
["2026-11-25-chatgpt-zapier", "ChatGPT conectado por Zapier para las ideas", "herramienta", "11-25", "Damián conectó ChatGPT (gpt-6-luna) a Claude por Zapier. Desde esta noche, en el reel diario ChatGPT propone 5 ideas, Claude otras 5 y se elige la mejor.", ["z_herr"]]
].forEach(r=>{if(!R.some(x=>x[0]===r[0])&&TY[r[2]])R.push(r);});
