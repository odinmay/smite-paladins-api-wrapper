# smite-paladins-api-wrapper
#
#
#### Wrapper for the Smite and Paladins Api, written in Python

Used for accessing the API to request various information about Hi-Rez studios two games
#
### How to use:
- Make an instance of `SmiteAPI(dev_id,auth_key)`
- Call a method to request the data you want

##### Example:
#
```sh
api = SmiteAPI(dev_id, auth_key)
api.get_gods()  #this returns your json data
```
That was easy!
#
Arguments for most methods are passed in as List[str], multiple arguments will be held in their own list
##### Example:   
## For Smite
```
api = SmiteAPI(dev_id, auth_key)
api.get_queue_stats(['Playername'], ['435'])
api.get_gods()
```
## For Paladins
```
api = PaladinsAPI(dev_id, auth_key)
api.get_bounty_items()
api.get_champions()
```
#

