expense-tracker-fastapi/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config/
│   │   └── security/
│   │
│   ├── database/
│   │   ├── session/
│   │   └── base/
│   │
│   ├── dependencies/
│   │   └── auth/
│   │
│   ├── features/
│   │   │
│   │   ├── auth/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   └── service/
│   │   │
│   │   ├── users/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   ├── service/
│   │   │   └── model/
│   │   │
│   │   ├── expenses/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   ├── service/
│   │   │   └── model/
│   │   │
│   │   ├── income/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   ├── service/
│   │   │   └── model/
│   │   │
│   │   ├── transactions/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   ├── service/
│   │   │   └── model/
│   │   │
│   │   ├── cards/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   ├── service/
│   │   │   └── model/
│   │   │
│   │   ├── dashboard/
│   │   │   ├── router/
│   │   │   ├── schemas/
│   │   │   └── service/
│   │   │
│   │   └── ai/
│   │       ├── router/
│   │       ├── schemas/
│   │       └── service/
│   │
│   └── shared/
│       ├── utils/
│       └── constants/
│
├── tests/
│   ├── auth/
│   ├── users/
│   ├── expenses/
│   ├── income/
│   ├── transactions/
│   ├── cards/
│   ├── dashboard/
│   └── ai/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md