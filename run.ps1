# Start the backend API in the background
Start-Process powershell.exe -ArgumentList "-NoExit -Command `"cd backend; .\venv\Scripts\activate; uvicorn main:app --reload`""

# Start the frontend dev server in the background
Start-Process powershell.exe -ArgumentList "-NoExit -Command `"cd frontend; npm run dev`""

Write-Host "Both servers are starting in new windows."
Write-Host "Backend API will be available at http://localhost:8000"
Write-Host "Frontend App will be available at http://localhost:5173"
