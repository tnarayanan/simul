# simul

*Python parallelism made simple*

simul makes your Python code run faster by running code simultaneously on your computer (parallelism).

Code becomes 8-10x faster (based on your specific computer) by running on multiple cores at once using Python no-GIL threading (Python 3.13t) or multiprocessing (Python 3.8 - 3.13, coming soon).

```python
import simul

users: list[User] = get_users()

# before simul
total_score = 0
for user in users:
  total_score += compute_user_score(user)
  
# with simul: 8-10x faster
total_score = simul.over(users, compute_user_score).reduce()

avg_score = total_score / len(users)

```

simul automatically verifies your code to check that it won't introduce non-determinism (when different orderings of code executions lead to different results) or race conditions (when multiple threads are accessing and modifying the same shared resource). This checker is in a primitive form right now, but will have more checks soon.

## Installation + Requirements

simul is available on PyPI as the package `simul`, and can be installed using Pip (`pip install simul`), uv (`uv add simul`), or any other equivalent installation process.

simul itself does not depend on external packages, but uses pytest for development tests.

simul currently runs only on Python 3.13t (the free-threaded version of Python 3.13) as its parallel execution backend depends on the lack of a GIL. The multiprocessing execution backend (coming soon) will using the `multiprocessing` standard library, and therefore support Python versions 3.8 - 3.13.
