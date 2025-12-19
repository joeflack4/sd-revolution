# SD Revolution
A Bundle of tools to help with the AI content generation creative process.

## Features
Some features (some of which may still be in development, or yet to be developed):
- Matrixify: Take as input a number of files or tables representing different prompt elements (plain text, LoRAs, etc),
and output either: (a) all of the ways these elements could be combined, or (b) a sample. 'b' might include a
recommender system as part of the implementation.
- Feedback mechanism: Take as input a set of file system paths, and create or update a representative interpretation.
The paths will include repositories of generated images or video, each one containing metadata about the prompts that
were used, etc. Directory structure itself, via the folder names, will include information such as categories and
subcategories, ratings, etc.

### Matrixify utility

Generate the Cartesian product of lines across multiple input files, concatenating each combination into a single output line.

**Parameters:**
- `--reverse` / `-r`: If True, reverse the nesting order so the first file varies slowest. This is useful when you want to primarily group output by the first file. For example, if the first file has two lines, the first half of the output will correspond to the first line, and the second half to the second line.
- `--and-split` / `-a`: If greater than 0, additionally write multiple output files (promptsN.txt). Each file will contain (number of lines in the first input file) divided by and_split.
- `--paths` / `-p`: Explicit list of input file paths.
- `--paths-glob` / `-P`: Glob pattern used to select input files. Defaults to "data/input/prompts*.txt" if neither `-p` nor `-P` is provided.
- `--output-file` / `-o`: Path to the main output file.

**Inputs:**
- N input files, each containing one or more lines.

**Outputs:**
- A single file containing the Cartesian product of all input lines, where each output line is formed by concatenating one line from each input file.

If there are N files, and file i has Li lines, the output will contain:
**L1 × L2 × ... × LN lines.**

**Example:**

Input files:
- file 1:
  ```
  abc, 123, yyy
  111, 222,
  ```

- file 2:
  ```
  lion, tiger,
  hippo, elephant,
  ```

- file 3:
  ```
  a,
  b, 12345,
  c, 6789,
  ```

Output:
```
abc, 123, yyy, lion, tiger, a,
abc, 123, yyy, lion, tiger, b, 12345,
abc, 123, yyy, lion, tiger, c, 6789,
abc, 123, yyy, hippo, elephant, a,
abc, 123, yyy, hippo, elephant, b, 12345,
abc, 123, yyy, hippo, elephant, c, 6789,
111, 222, lion, tiger, a,
111, 222, lion, tiger, b, 12345,
111, 222, lion, tiger, c, 6789,
111, 222, hippo, elephant, a,
111, 222, hippo, elephant, b, 12345,
111, 222, hippo, elephant, c, 6789,
```

### Image Metadata Reader utility

Extract metadata from AI-generated images (primarily Stable Diffusion images) and save in both raw text and structured JSON formats.

**Parameters:**
- `--input` / `-i`: Input image file path (required)
- `--txt-output` / `-t`: Output text file path for raw metadata (required)
- `--json-output` / `-j`: Output JSON file path for structured metadata (required)

**Inputs:**
- An image file (PNG format recommended, commonly from Stable Diffusion or similar AI image generators)

**Outputs:**
- **Text file**: Contains the raw metadata exactly as stored in the image
- **JSON file**: Contains structured metadata with parsed fields:
  - `prompt`: The positive prompt used to generate the image (multi-line supported)
  - `negative_prompt`: The negative prompt (multi-line supported)
  - `parameters`: Dictionary of generation parameters (Steps, Sampler, CFG scale, Seed, Model, etc.)
  - `raw`: The complete raw metadata string

**Example usage:**

```bash
python -m sd_revolution extract-metadata -i image.png -t metadata.txt -j metadata.json
```

**Example output (JSON):**

```json
{
  "prompt": "<lora:style_lora:1>, character portrait, detailed face",
  "negative_prompt": "blurry, low quality, distorted",
  "parameters": {
    "Steps": 23,
    "Sampler": "Euler a",
    "CFG scale": 7,
    "Seed": 3208283879,
    "Size": "512x768",
    "Model": "model_name",
    "Version": "v1.9.4"
  },
  "raw": "<complete raw metadata string>"
}
```

The utility automatically handles:
- Multi-line prompts and negative prompts
- Various parameter types (integers, floats, strings)
- Quoted values in parameters (e.g., Lora hashes)
- Different metadata formats from various Stable Diffusion implementations