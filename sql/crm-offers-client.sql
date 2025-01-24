SELECT
    c.client_id AS numer_teczki,
    c.short_name AS nazwa_skrócona,
    e.employees_collection AS handlowiec,
    e.event_type_id AS typ,
    e.description AS opis,
    CAST(e.event_date AS DATE) AS data

FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id
WHERE e.event_type_id = 'offer' AND c.client_id = '76339'
ORDER BY  e.event_date, e.employees_collection

;
