pandoc --from=markdown --to=latex --standalone --output=output.tex README.md

Image conversion: 
`rsvg-convert input.svg -o output.png`


rsvg-convert graph_fully_con.svg -o graph_fully_con.png
rsvg-convert KG_Architecture.svg -o KG_Architecture.png
rsvg-convert TransE_Goal.svg -o TransE_Goal.png
rsvg-convert TransE_training.svg -o TransE_training.png
rsvg-convert Application_Architecture.svg -o Application_Architecture.png