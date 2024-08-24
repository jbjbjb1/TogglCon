import json

a= json.dumps({"Data": [
            {
                "Date": f"date",
                "Branch": f"emailname",
                "Charge Type": "ABCABCAB-AB",
                "Project No": f"togglapikey",
                "Job No": "ABC0001111",
                "Description": "(Client) Planning",
                "Hours": "3.5"
            },
            {
                "Date": "05/04/24",
                "Branch": "Branch 1",
                "Charge Type": "TYPE 1",
                "Project No": "PROJ 2",
                "Job No": f"workspace_ID",
                "Description": "First aid training (3.5hr)",
                "Hours": "3.5"
            }
            ]
            })

b = ({"Data": [
            {
                "Date": f"date",
                "Branch": f"emailname",
                "Charge Type": "ABCABCAB-AB",
                "Project No": f"togglapikey",
                "Job No": "ABC0001111",
                "Description": "(Client) Planning",
                "Hours": "3.5"
            },
            {
                "Date": "05/04/24",
                "Branch": "Branch 1",
                "Charge Type": "TYPE 1",
                "Project No": "PROJ 2",
                "Job No": f"workspace_ID",
                "Description": "First aid training (3.5hr)",
                "Hours": "3.5"
            }
            ]
            })

print('')