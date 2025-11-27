from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origin ที่อนุญาตให้เรียกได้
origins = [
    "http://localhost:3000",          # ตอน dev frontend รันที่นี่
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com"  # ถ้ามี domain จริง ให้ใส่เพิ่ม
    # จะเพิ่ม origin อื่นได้อีก เช่น mobile/web app อื่น ๆ
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # หรือ ["*"] ถ้าจะเปิดโล่ง (ใช้เฉพาะตอน dev)
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE ทั้งหมด
    allow_headers=["*"],            # อนุญาตทุก header เช่น Authorization, Content-Type
)


@app.get("/")
def read_root():
    return {"message": "Hello from Cloud Run! Hey 123"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"message": "This is a test message"}
