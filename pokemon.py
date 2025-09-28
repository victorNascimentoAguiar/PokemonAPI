#importa a funcao REQUESTS
import requests
from deep_translator import GoogleTranslator
#https://pokeapi.co/api/v2/pokemon-species/{id or name}/

def get_type_weaknesses(types):
    weaknesses = []
    resistances  = []
    immunities = []

    for t in types :
        url = f"https://pokeapi.co/api/v2/type/{t}"
        res = requests.get(url)
        if res.status_code !=200:
            continue
        type_data = res.json()

        #add fraqueza
        for w in type_data["damage_relations"]["double_damage_from"]:
            weaknesses.append(w["name"])
        #add resistencia
        for r in type_data["damage_relations"]["half_damage_from"]:
            resistances.append(r["name"])
        #add imunidade
        for i in type_data["damage_relations"]["no_damage_from"]:
            immunities.append(i["name"])
            
    #remover duplicidades
    weaknesses = list(set(weaknesses))
    resistances = list(set(resistances))
    immunities = list(set(immunities))

    return {
        "weaknesses" : weaknesses,
        "resistances" : resistances,
        "immunities" : immunities
    }

def pokemon_Dex(name_or_id):
    #busca os dados do pokemon
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name_or_id}"
    species_res = requests.get(species_url)
    if species_res.status_code != 200:
        return None    
    species_data = species_res.json() 

    # buscando nome e ID do pokemon  
    name = species_data["name"]
    id_ = species_data["id"]

    #traduz para portuques a descricao do pokemon
    description = None
    for entry in species_data["flavor_text_entries"]:
        if entry["language"]["name"] == "en":
            description = entry ["flavor_text"].replace("\n", " ").replace("\f", " ")
            break
    if description:
        description = GoogleTranslator(source="en", target="pt").translate(description)
    # pokemon data (tipos, stats, entre outras coisas)
    pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id}"
    pokemon_res = requests.get(pokemon_url)
    pokemon_data = pokemon_res.json() if pokemon_res. status_code == 200 else {}


    #buscando o tipo do pokemon 
    types = [t["type"]["name"] for t in pokemon_data["types"]]
    #busca a fraquesa,forca e imunidade dos pokemons
    damage_relations = get_type_weaknesses(types)
    





    

    #busca cadeia evolutiva
    evo_chain_url = species_data["evolution_chain"]["url"]
    evo_res = requests.get(evo_chain_url)
    if evo_res.status_code != 200:
        evolution = []
    else:
        evo_data = evo_res.json()["chain"]


    # funcao recursiva para buscar evolucoes
        evolutions = []
        #definindo uma funcao que busca a cadeia evolutiva do pokemon como por exemplo charmander > charmeleon > chalizard
        def extract_chain(chain):
            current = {"name": chain["species"]["name"], "envolves_to": []}
            evolutions.append(chain["species"]["name"])
            #FOR para procurar a cadeia evolutiva dos pokemons
            for evo in chain.get("evolves_to", []):       
                #detalhe da evolucao
                detalhe_evo = evo.get("evolution_details", [])
                condition = []
                #FOR para veririficar a  maneira que o pokemon evolui
                for d in detalhe_evo:
                    if d.get("trigger"):
                        condition.append(f"trigger: {d['trigger']['name']}")
                    if d.get("item"):
                        condition.append(f"item: {d['item']['name']}")
                    if d.get("min_level"):
                        condition.append(f"min_level: {d['min_level']}")
                    if d.get("time_of_day") and d["time_of_day"] != "":
                        condition.append(f"time_of_day: {d['time_of_day']}")
                    if d.get("known_move"):
                        condition.append(f"known_move: {d['known_move']['name']}")
                current["envolves_to"].append({
                    "name": evo["species"]["name"],
                    "conditions": condition
                })
                #cadeia recursiva para caso o pokeon tiver varios tipos de evolucao como por exemplo o EEVEE que tem varias eevelutions 
                current["envolves_to"][-1].update(extract_chain(evo))
            #retorna os itens em questao
            return current

            
        
        # inicia a extração
        extract_chain(evo_data)
 

    


    #retorna os dados obtidos
    return{
    "name": name,
    "id" : id_,
    "description" : description,
    "types" : types,
    "damage_relations": damage_relations,
    "evolution_chain": extract_chain(evo_data)
    }

def print_tipo_fraquesa_resistancia_imunidade(pokemon):
    print("Tipos:", ", ".join(pokemon["types"]))
    print("Fraquezas:", ", ".join(pokemon["damage_relations"]["weaknesses"]))
    print("Resistências:", ", ".join(pokemon["damage_relations"]["resistances"]))
    print("Imunidades:", ", ".join(pokemon["damage_relations"]["immunities"]))



#esta melhorando a forma que o a cadeia evolutiva e exibida para evitar confusoes 
def print_cadeia_evolutiva(chain, indent=0):
    spaces = "  " * indent
    #mostrar o nomem do pokemon
    print(f"{spaces}- {chain['name']}")
    #caso tenha condicao para evoluir
    if "conditions" in chain and chain["conditions"]:
        for cond in chain["conditions"]:
            #simbolo bonitionha copiado da net:  ↳
            print(f"{spaces}   ↳{cond}")
    #repete para cada evolucao
    for evo in chain.get("envolves_to", []):
        print_cadeia_evolutiva(evo, indent +1)

#input do usuario 
#usuario vai escolher qual pokemon ele quer procurar

pokemon_usuario = input("digite o nome ou  numero na dex do pokemon:  ").lower()
pokemon= pokemon_Dex(pokemon_usuario)

#retorna o pokemon que o usuario buscou e suas informacoes.
if pokemon:
    print("nome: ", pokemon["name"])
    print("id: ", pokemon["id"])
    print("Cadeia evolutiva: ")
    print_cadeia_evolutiva(pokemon["evolution_chain"])
    print("descricao:", pokemon["description"])
    print_tipo_fraquesa_resistancia_imunidade(pokemon)
    
#caso nao encontre o pokemon ele retorna um aviso falando que o pokemon nao foi encontrado
else:
    print("pokemon nao localizado")









#teste teste teste


#antiga funcao para buscar pokemons porem muito bruta nao serve para oque etou fazendo agora;
#Porem gostaria de quardar para estudos futuros. 
#descartada por trazer todos os dados de uma vez tornando inefiiente 



"""   

#definindo a funcao da API
#def pokemon_name(endpoint, identifier=""):
    #url = f"https://pokeapi.co/api/v2/{endpoint}/{identifier}"
    #response = requests.get(url, params=identifier)
    #return response.json() if  response.status_code == 200 else None
## utilizando o def para buscar os dados da API
pokemonSpecies = pokemon_name("pokemon-species/","600") 
##Pede ao usuario para escolher ou nome do pokemon ou ID(Numero na pokedex)


##verifica se  o dado e valido e retorna o item selecionado
if pokemonSpecies:
    print(pokemonSpecies)
else:
    print("pokemon not fould")

"""  









