SELECT
    c.client_id AS numer_teczki,
    c.short_name AS nazwa_skrócona,
    e.employees_collection AS handlowiec,
    e.event_type_id AS typ,
    c.full_name AS nazwa_firmy,
    e.description AS opis,
    c.city AS miasto,
    c.area_name AS wojewodztwo,
    e.event_date AS data
FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id
WHERE
    (
        (e.event_type_id = 'offer' OR e.event_type_id = 'VISIT' OR e.event_type_id = 'contact' OR e.event_type_id = 'note')
        # e.event_type_id = 'offer'
        # AND e.employees_collection LIKE '%%'
        AND (e.description LIKE '%używan%' AND e.description LIKE '%kruszar%')
       #AND (e.description LIKE '%JAWMAX%' OR e.description LIKE '%REMAX%' or e.description LIKE '%keestrack b%' or e.description LIKE '%keestrack r')
        # AND e.event_date BETWEEN'2023-01-01 00:00:00' and '2023-11-30 00:00:00'
    )
ORDER BY e.employees_collection, e.event_type_id;