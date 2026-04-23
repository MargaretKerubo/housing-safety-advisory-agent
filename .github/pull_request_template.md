## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement (improvement to existing feature)
- [ ] Refactor (no functional changes)
- [ ] Documentation
- [ ] CI/Build/Config


## What changed and why

<!-- Briefly describe what this PR does and the motivation behind it. -->


## How to test

<!-- Steps a reviewer can follow to verify the changes work. -->

1. 


## Checklist

- [ ] Tested locally
- [ ] No new environment variables (or `.env.example` updated)
- [ ] Database migrations included if schema changed
- [ ] No sensitive data committed


---

## Commit Message Rules (MANDATORY)

Format:
type: short description  
or  
type(scope): short description  

### Allowed types (must match PR type):

- fix → Bug fix  
- feat → New feature  
- feat → Enhancement  
- refactor → Refactor  
- docs → Documentation  
- ci / build / config → CI/Build/Config  

### Rules:
- lowercase only
- max 72 characters
- present tense
- no vague messages (e.g. "update", "stuff")

### Examples:
- feat(auth): add login endpoint
- fix(api): handle null response
- refactor(ui): clean dashboard layout


Closes #
