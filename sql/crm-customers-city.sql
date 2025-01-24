SELECT client_id as 'teczka', full_name 'Nazwa', city 'Miasto'
FROM `crm`.`clients`
# WHERE crm.clients.area_name = 'Małopolskie'
where area_id = 'mlp'
ORDER BY 2, 3
;
