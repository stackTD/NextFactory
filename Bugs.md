----------------------------------------------------------------------------------------- On dashboard page
-- Clicked "system help", app crashed

Error:
File "C:\StackLeaderShip\Softwares\nextFactory\research\NextFactory\main.py", line 492, in show_help
Current User: {self.user.get_full_name()}
^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\StackLeaderShip\Softwares\nextFactory\research\NextFactory\models.py", line 203, in get_full_name
return f"{self.first_name} {self.last_name}"
^^^^^^^^^^^^^^^
File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 566, in get
return self.impl.get(state, dict_) # type: ignore[no-any-return]
^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1086, in get
value = self._fire_loader_callables(state, key, passive)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1116, in _fire_loader_callables
return state._load_expired(state, passive)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\state.py", line 798, in _load_expired
self.manager.expired_attribute_loader(self, toload, passive)
File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\loading.py", line 1584, in load_scalar_attributes
raise orm_exc.DetachedInstanceError(
sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x1eab25e9340> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)


------------------------------------------------------------------------------------------------ Inventory manager page

-- In filter section [all option in filter are causing crash]: Clicked and Selected "category":: app crashed

Error: 
INFO:database:Database engine created: DatabaseConfig(host='localhost', port='5432', database='nextfactory', user='nextfactory')
Traceback (most recent call last):
  File "C:\StackLeaderShip\Softwares\nextFactory\research\NextFactory\erp_modules.py", line 313, in apply_filters
    if item.category.value == category_value]
       ^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1116, in _fire_loader_callables
    return state._load_expired(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\state.py", line 798, in _load_expired
    self.manager.expired_attribute_loader(self, toload, passive)
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\loading.py", line 1584, in load_scalar_attributes 
    raise orm_exc.DetachedInstanceError(
sqlalchemy.orm.exc.DetachedInstanceError: Instance <InventoryItem at 0x1a90324e6f0> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)


-- Clicked search below category:: App crashed
-- Click "Show only low stock check button":: App crashed

------------------------------------------------------------------------------------------------------ Production Scheduling

-- Click "Status Fliter" App crashed:
Error:

Traceback (most recent call last):
  File "C:\StackLeaderShip\Softwares\nextFactory\research\NextFactory\mes_modules.py", line 429, in apply_task_filter
    filtered_tasks = [t for t in filtered_tasks if t.status.value == status_value]
                                                   ^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\attributes.py", line 1116, in _fire_loader_callables
    return state._load_expired(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\state.py", line 798, in _load_expired
    self.manager.expired_attribute_loader(self, toload, passive)
  File "C:\Users\sltri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\sqlalchemy\orm\loading.py", line 1584, in load_scalar_attributes
    raise orm_exc.DetachedInstanceError(
sqlalchemy.orm.exc.DetachedInstanceError: Instance <ProductionTask at 0x2578a5e41a0> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)

- clicked priority: App Crashed

----------------------------------------------------------------------------------------------------------Quality Management

- Clicked Filter by result: App crashed

