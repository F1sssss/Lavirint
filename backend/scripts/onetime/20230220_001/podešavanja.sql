-- Custom document upload settings
SET @firma_id = 241;
UPDATE 
    firma 
SET 
    ima_upload_dokumenta=1, 
    dokument_qr_code_x=15, 
    dokument_qr_code_y=120,
    dokument_qr_code_width=30,
    dokument_qr_code_height=30,
    dokument_ikof_x=50,
    dokument_ikof_y=120,
    dokument_jikr_x=50,
    dokument_jikr_y=125,
    dokument_efi_verify_url_x=50,
    dokument_efi_verify_url_y=130,
    dokument_kod_operatera_x=50,
    dokument_kod_operatera_y=135
WHERE 
    id=@firma_id;

-- Invoice schedule settings
SET @firma_id = 241;
UPDATE company_settings SET can_schedule=1 WHERE company_id=@firma_id;


-- SOAP User
SET @firma_id = 241;
SET @username = 'digital';
SET @password = '$pbkdf2-sha256$29000$I6Q0Zsz5n7O29t77H2MMYQ$z6R4alc6xHAMBHkhV9dwKPCSKAI94/8h8xPhZtXCKAA';

INSERT INTO soap_user (username, password, is_active) VALUES (@username, @password, 1);
SET @soap_user_id = LAST_INSERT_ID();

INSERT INTO soap_permission (company_id, soap_user_id) VALUES (@firma_id, @soap_user_id);