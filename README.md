# smallworld

A minimal model of communication as distributed computation among
heterogeneous finite agents. See MISSION.md (frozen), DESIGN.md (accepted) and
LOG.md (append-only).

```
python -m smallworld.run configs/e1.toml            # writes results/e1/
python -m smallworld.summarize results/e1           # windowed means
python -m unittest discover tests                   # degenerate limits
```

Interfaces live in `smallworld/core/`, default implementations in
`smallworld/impl/`. A config names the class for each component.
