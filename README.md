# brainfuck-txt
Uses Python to generate compact code in the brainfuck programming language displaying the contents of a specified .txt file.

The obvious purpose of this project is to compress the Bee Movie Script into as few bytes of brainfuck code as possible.

## Usage
Specify the path of the txt file to be encoded in the topmost Section of the script, `"beemovie.txt"` by default.
Different encoding algorithms, typically ranked from worst to best, are used to encode the text into brainfuck. The resulting file `beemovie.b` can be used with any brainfuck interpreter set to 8 bit mode with wraparound enabled.

## The compression explained
Typically, text files in English contain characters that are not randomly distributed but in a rather predictable range. The characters are interpreted as numbers from 0x00 to 0x7F and in most cases it is optimal to find two possible preset values for the character's corresponding memory cell that result in the lowest possible average variance to them from any given character, so less operations are needed to get the final result.
The lower one of these values can be copied to as many memory cells as there are characters in the text using a constant (and relatively low) amount of instructions with a few tricks.
The higher value can be added onto all applicable memory cells in about 1n to 2n brainfuck instructions for n characters.
This leaves all memory cells close enough to their intended values for comparatively few `+` and `-` operations to be necessary before each cell's value can be printed to the console as a character.

Basically this takes advantage of the fact that *filling* a lot of memory cells with a value takes almost no instuctions at all, additively *copying* memory cells takes very few instuctions and *creating* numbers from scratch, even with multiplicative loops and wraparound tricks, takes the most operations.

The compressed text is still about 10x the size of the original text, but that's still slightly less than [the most efficient implementation I found online.](https://copy.sh/brainfuck/text.html)

## Practical applications
¯\\_(ツ)_/¯
beat my compression highscore I guess

## License & Credits
[Original brainfuck interpreter used](https://github.com/pocmo/Python-Brainfuck)
[Licensed under the MIT License, © 2021 Julian Karrer](https://opensource.org/licenses/MIT)
