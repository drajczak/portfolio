SELECT
    c.client_id AS numer_teczki,
    c.short_name AS nazwa_skrócona,
    e.employees_collection AS handlowiec,
    e.event_type_id AS typ,
    c.full_name AS nazwa_firmy,
    e.description AS opis,
    c.city AS miasto,
    e.event_date AS data,
    c.rank As kategoria
FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id
WHERE
    (
        (e.event_type_id = 'offer' OR e.event_type_id = 'VISIT' OR e.event_type_id = 'contact' OR e.event_type_id = 'note')
        AND e.employees_collection LIKE '%klup%'
        # AND e.added_by_employee_id like '%%'
        # AND e.event_date = '2023-09-21 00:00:00'
        AND e.event_date BETWEEN'2024-04-01 00:00:00' and '2024-04-30 00:00:00'
    )
ORDER BY e.employees_collection, e.event_type_id
;