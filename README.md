### Stock Portfolio Management Tool Repo of Backend

Huaize Ye yhz613609@gmail.com huaizeye@usc.edu  
Yuxuan Ren yuxuanre@usc.edu  
Haochen Li sznxlhc0205@gmail.com hli61559@usc.edu  

##### [Website deployed on Azure](https://purple-bush-0fbcbce1e.5.azurestaticapps.net/#/register)
##### [Link to Frontend Repo](https://github.com/HuaizeUSC/stock-portfolio-frontend)

Tech stack:React, Django, JavaScript, Python, Redux, Tailwind CSS, MySQL, Vite

#### Function

1. Initialize System with NasDaq100
2. Create and Update Stock Model(Support All US Market)
3. User Management with Token system
4. Fetch Real Time Data from Polygon
5. Distributed Store System Management
6. Secure API with Authorization

#### Backend
##### Main File structure
- /Stock-Protfolio-Management-Tool
  - /stock_tool
    - /stock (stock related files)
    - /stock_tool (django setting files)
    - /templates
    - /user (user related files)
    - db1.sqlite3
    - db2.sqlite3
    - db3.sqlite3
    - db.bat
  - .gitattributes

#### Instruction
1. Install Python & Django
2. clone repo  
`git clone https://github.com/HuaizeUSC/Stock-Portfolio-Management-Tool.git`
3. Install dependencies  
`cd stock_tool`  
`pip install -r requirements.txt`  
4. Migrate database  
`./db.bat`
5. Start backend server  
`python manage.py runserver`
