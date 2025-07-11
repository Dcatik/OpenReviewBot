from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str
    registration_date: str


@dataclass
class Company:
    company_id: int
    name: str


@dataclass
class Review:
    review_id: int
    company_id: int
    user_id: int
    rating: int
    review_text: str
    status: str
    date: str