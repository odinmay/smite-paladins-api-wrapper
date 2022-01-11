from smite_api_wrapper import SmiteAPI
from smite_api_wrapper import devId, authKey
import pandas as pd
from collections import defaultdict


def create_god_data_csv(json_data):
    """Takes in the json data from the get_gods api request
    and creates a formatted csv file with comma delimiter
    and pickled pandas Dataframe object"""

    # Names for defaultdict keys
    key_names = ['Name',
                 'Title',
                 'Pantheon',
                 'Type',
                 'Roles',
                 'Speed',
                 'Health',
                 'HealthPerFive',
                 'HP5PerLevel',
                 'HealthPerLevel',
                 'basicAttack',
                 'Mana',
                 'ManaPerFive',
                 'MP5PerLevel',
                 'ManaPerLevel',
                 'AttackSpeed',
                 'AttackSpeedPerLevel',
                 'PhysicalPower',
                 'PhysicalPowerPerLevel',
                 'MagicalPower',
                 'MagicalPowerPerLevel',
                 'PhysicalProtection',
                 'PhysicalProtectionPerLevel',
                 'MagicProtection',
                 'MagicProtectionPerLevel'
                 ]

    # Create main defaultdict with list factory
    dictionary = defaultdict(list)

    # For every god, run every key operation to build data dict
    for god in json_data:
        for key in key_names:

            # Unpack basicAttack dictionary
            # Magic and Power basic attacks scale differently
            if key == 'basicAttack':

                # Magic Power Basic dmg 1-20
                if 'Magical' in god['Type']:
                    dmg_per_level = \
                        god['basicAttack']['itemDescription']['menuitems'][0]['value'][:12].split('/')[0].split(' ')[2]

                    for num in range(1, 21):
                        dictionary[f'BasicAttack_L{num}'].append(
                            round(float(god['basicAttack']['itemDescription']['menuitems'][0]['value'][:2]) + (
                                        float(dmg_per_level) * (-1 + num)), 2))

                # Physical Power Basic dmg 1-20
                elif 'Physical' in god['Type']:
                    for num in range(1, 21):
                        dictionary[f'BasicAttack_L{num}'].append(
                            round(float(god['PhysicalPower']) + (float(god['PhysicalPowerPerLevel']) * (-1 + num)),
                                  2))

            # Calculate Health Level 1-20
            elif key == 'Health':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(int(god[key]) + (int(god['HealthPerLevel']) * (-1 + num)))

            # Calculate HP5 Level 1-20
            elif key == 'HealthPerFive':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['HP5PerLevel']) * (-1 + num)), 2))

            # Calculate Mana Level 1-20
            elif key == 'Mana':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(int(god[key]) + (int(god['ManaPerLevel']) * (-1 + num)))

            # Calculate MP5 Level 1-20
            elif key == 'ManaPerFive':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['MP5PerLevel']) * (-1 + num)), 2))

            # Calculate Attack Speed Level 1-20
            elif key == 'AttackSpeed':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['AttackSpeedPerLevel']) * (-1 + num)), 2))

            # Calculate Physical Power Level 1-20
            elif key == 'PhysicalPower':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['PhysicalPowerPerLevel']) * (-1 + num)), 2))

            # Calculate Physical Protection Level 1-20
            elif key == 'PhysicalProtection':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['PhysicalProtectionPerLevel']) * (-1 + num)), 2))

            # Calculate Magic Protection Level 1-20
            elif key == 'MagicProtection':
                for num in range(1, 21):
                    dictionary[key + f'_L{num}'].append(
                        round(float(god[key]) + (float(god['MagicProtectionPerLevel']) * (-1 + num)), 2))

            # Add all other stats that don't scale with level
            else:
                dictionary[key].append(god[key])

    # Build dataframe from dictionary
    df = pd.DataFrame().from_dict(dictionary)

    # Output to csv file
    df.to_csv('god_data.csv')

    # Serialize dataframe to pickle obj
    df.to_pickle('god_data_df.pkl')


if __name__ == '__main__':
    # Instantiate SmiteApi Object with credentials
    api = SmiteAPI(devId, authKey)

    # Call function with the returned json from the get_gods endpoint
    create_god_data_csv(api.get_gods())
