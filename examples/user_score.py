import simul

class User:
    ...

def get_users() -> list[User]:
    ...



def compute_user_score(user: User) -> float:
    ...

users: list[User] = get_users()
total_score = simul.over(users, compute_user_score).reduce()
avg_score = total_score / len(users)

def body(elem: str) -> int:
  return len(elem)
  
simul.over(range(10), body).reduce()
