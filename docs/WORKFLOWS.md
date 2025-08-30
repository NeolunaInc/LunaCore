
Workflows Project (GitHub)
1) Item added to project — Issues uniquement
Type : Issue ✅ | Pull request ❌

Action : Set value → Status = Backlog

Toggle : On

2) Item reopened
Action : Set value → Status = Backlog

Toggle : On

3) Item closed
Action : Set value → Status = Terminé

Toggle : On

4) Auto-add to project (ajout auto)
Repository : NeoLunaInc/LunaCore

Query : is:issue (optionnel is:open)

Action : Add the item to the project

Si l’UI exige un Set value, choisir Status=Backlog.

5) Pull request merged
Action : Set value → Status = Terminé

Toggle : On

6) Auto-close issue
Trigger : When the status is updated

Filtre : Status: Terminé

Action : Close the issue

Toggle : On

7) Auto-archive items (optionnel)
Filtre : is:issue is:closed updated:<@today-2w

Action : Archive item

Toggle : On

Astuce tri : ajouter un champ Number nommé PhaseNo, le renseigner, puis Sort by PhaseNo (ascending) sur la Board.
