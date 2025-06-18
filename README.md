# PHIL-4176

# Build web app

```bash
cd /src
npm install
npm run build
```

# The Backend

The backend relies on azure functions. Point azure functions to api directory. You must also set the GOOGLE_API_KEY environment variable to your Google API key.

Be sure to install the necessary dependencies for the backend:

```bash
cd /api
pip install -r requirements.txt
```

# $\LaTeX$ Paper

This paper is typeset using $\LaTeX$. It is based on the template provided at https://github.com/pmichaillat/latex-paper. 

To build the paper, run the following command:

```bash
cd /paper
pdflatex paper
bibtex paper
pdflatex paper
pdflatex paper
```