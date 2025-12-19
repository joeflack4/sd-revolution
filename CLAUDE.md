# Agent guide
## Project overview
The project is called "SD Revolution", and is a bundle of tools to help with the AI content generation creative process.

Some features (some of which may still be in development, or yet to be developed):
- Matrixify: Take as input a number of files or tables representing different prompt elements (plain text, LoRAs, etc),
and output either: (a) all of the ways these elements could be combined, or (b) a sample. 'b' might include a 
recommender system as part of the implementation. 
- Image metadata reader: Input is an image, and output is structured metadata.
- Feedback mechanism: Take as input a set of file system paths, and create or update a representative interpretation. 
The paths will include repositories of generated images or video, each one containing metadata about the prompts that 
were used, etc. Directory structure itself, via the folder names, will include information such as categories and 
subcategories, ratings, etc.
