# Publishing Guide: Pushing InvoiceFlow to GitHub

## Option 1: Upload via GitHub Web Interface (Fastest)
1. Extract `InvoiceFlow_GitHub_Ready.zip` on your computer.
2. Open the extracted `InvoiceFlow` folder so you see `src`, `tests`, `README.md`, etc.
3. Go to your new GitHub repository in your browser and click **uploading an existing file**.
4. Drag and drop all files and folders from inside `InvoiceFlow` into the upload area.
5. Add commit message `Initial commit: InvoiceFlow structured invoice extraction pipeline` and click **Commit changes**.

## Option 2: Push via Git CLI
```bash
cd InvoiceFlow
git init
git add .
git commit -m "Initial commit: InvoiceFlow structured invoice extraction pipeline"
git branch -M main
git remote add origin https://github.com/Rasheena-Arimbrathodi/<your-new-repo>.git
git push -u origin main
```
