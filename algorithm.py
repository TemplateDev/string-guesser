from collections.abc import Callable
import random


def mutate(
    objective: Callable[[str], float],
    string: str,
    charset: tuple[str, ...],
    evaluated: set[str],
) -> tuple[str, float, set[str]]:
    current_score = objective(string)
    best_candidate = string
    best_score = current_score

    for position in range(len(string)):
        for replacement in charset:
            candidate = string[:position] + replacement + string[position + 1 :]
            if candidate == string or candidate in evaluated:
                continue

            evaluated.add(candidate)
            candidate_score = objective(candidate)
            if candidate_score > best_score:
                best_candidate = candidate
                best_score = candidate_score
                break
            else:
                continue

    return best_candidate, best_score, evaluated


class Solver:
    def __init__(
        self,
        initial_string: str,
        charset: tuple[str, ...],
        objective_fn: Callable[[str], float],
        population_size: int = 100,
        seed: int | None = None,
    ) -> None:
        if population_size < 2:
            raise ValueError("population_size must be at least 2")

        self.guess = initial_string
        self.objective = objective_fn
        self.score = self.objective(self.guess)
        self.charset = charset
        self.population_size = population_size
        self.random = random.Random(seed)

    def run(
        self,
        iterations: int = 100_000,
        steps: int = 1000,
        on_iteration: Callable[[int, str, float], None] | None = None,
        target_score: float | None = None,
    ) -> tuple[str, float]:
        if on_iteration is not None and steps <= 0:
            raise ValueError("steps must be greater than zero when on_iteration is set")
        if self.guess and not self.charset:
            raise ValueError("charset must not be empty for a non-empty guess")

        population = [self.guess]
        population.extend(
            "".join(
                self.random.choice(self.charset)
                for _ in range(len(self.guess))
            )
            for _ in range(self.population_size - 1)
        )
        best_guess, best_score = self.guess, self.score
        completed_iterations = 0
        last_reported_iteration = 0
        elite_count = max(1, self.population_size // 10)
        mutation_rate = 1 / max(1, len(self.guess))

        for i in range(1, iterations + 1):
            scored_population = [
                (candidate, self.objective(candidate))
                for candidate in population
            ]
            scored_population.sort(key=lambda item: item[1], reverse=True)
            generation_best, generation_score = scored_population[0]
            if generation_score > best_score:
                best_guess, best_score = generation_best, generation_score

            completed_iterations = i
            reached_target = target_score is not None and best_score >= target_score
            if on_iteration is not None and (
                i % steps == 0 or reached_target
            ):
                on_iteration(i, best_guess, best_score)
                last_reported_iteration = i

            if reached_target:
                break

            next_population = [
                candidate for candidate, _ in scored_population[:elite_count]
            ]
            while len(next_population) < self.population_size:
                parent_a = self._select_parent(scored_population)
                parent_b = self._select_parent(scored_population)
                child = [
                    self.random.choice((char_a, char_b))
                    for char_a, char_b in zip(parent_a, parent_b)
                ]
                for position, character in enumerate(child):
                    if self.random.random() < mutation_rate and self.charset:
                        replacement = self.random.choice(self.charset)
                        if replacement != character:
                            child[position] = replacement
                next_population.append("".join(child))
            population = next_population

        if on_iteration is not None and completed_iterations != last_reported_iteration:
            on_iteration(completed_iterations, best_guess, best_score)

        self.guess, self.score = best_guess, best_score
        return best_guess, best_score

    def _select_parent(
        self,
        population: list[tuple[str, float]],
        tournament_size: int = 3,
    ) -> str:
        contestants = self.random.sample(
            population,
            min(tournament_size, len(population)),
        )
        return max(contestants, key=lambda item: item[1])[0]
