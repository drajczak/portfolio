SELECT COUNT(*) 'Ilość', e.employees_collection as 'Pracownik', e.event_type_id as 'rodzaj'
FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id
WHERE e.event_type_id LIKE '%%'
# AND e.added_by_employee_id like '%%'
# AND employees_collection NOT LIKE '%p.kucz%' 
AND (
	employees_collection LIKE '%p.ku%'
    OR
    employees_collection LIKE '%oche%')
# AND employees_collection NOT LIKE '%j.ku%'
AND e.event_date BETWEEN '2024-05-01 00:00:00' AND '2024-05-31 00:00:00'
# AND e.event_date = '2023-08-22 00:00:00'
GROUP BY e.employees_collection, e.event_type_id
ORDER BY e.employees_collection, e.event_type_id
;