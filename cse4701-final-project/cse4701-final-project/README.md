# cse2102-Spring25-Team26
Nauman Chaudhary Nac20034
Jie Chen jic22015
Thomas Maceira tcm22005
Megan Bjunes meb19011
https://trello.com/b/04gZ6ZBt/2102-group-project

https://www.figma.com/design/QXFaitMwtoeJ2BJlz3ytIG/Untitled?node-id=0-1&p=f&t=yUVFZwIS45xbnjYN-0


# Pet Adoption Group Project

## Backend Setup

### 1. Install Dependencies (without Docker)
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt


## Running the Application

### Backend
#### Local
```bash
cd backend
pip install -r requirements.txt
python main.py

Docker
cd backend
docker build -t team26-petadoption-api .
docker run -p 5000:5000 team26-petadoption-api

Frontend

local

cd frontend
npm install
npm run dev

Open: http://localhost:3000

Docker

cd frontend
docker build -t team26-petadoption-frontend .
docker run -p 80:80 team26-petadoption-frontend

Open: http://localhost

This ensures your TA can run both containers together:
```bash
docker network create pet-net
docker run -d --name backend --network pet-net team26-petadoption-api
docker run -d -p 80:80 --network pet-net team26-petadoption-frontend
