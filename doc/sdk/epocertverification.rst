ePO Certificate Verification
============================

The ePO DXL service supports validating the authenticity of the certificate associated with each ePO server that is
being connected to.

Enabling and disabling of this capability is controlled via the ``verifyCertificate`` property that is associated with
each ePO server defined within the server configuration file
(see :ref:`Service Configuration File <dxl_service_config_file_label>`). While this validation can be disabled, it
is highly recommended that it be enabled for production environments.

The remainder of this page walks through the steps necessary to obtain the information required to perform this
validation successfully.

Two types of certificate validation take place when connecting to an ePO server:

1. The ``host`` as defined in the service configuration file for the ePO server must match the hostname in the
   ePO server's certificate.
2. The ePO server's certificate must be signed by a Certificate Authority (CA) that can be found in the
   CA bundle (specified via the ``verifyCertBundle`` property) associated with the ePO server in the service
   configuration file.

To determine the hostname in the ePO server's certificate and the certificate of the signing CA you can execute
the following command via ``openssl``.

    .. parsed-literal::

        openssl s_client -showcerts -connect <epo-host>:<epo-port>

For example:

    .. parsed-literal::

        openssl s_client -showcerts -connect epotestsystem:8443

The output of the command should appear similar to the following:

    .. parsed-literal::

        CONNECTED(00000003)
        depth=1 O = McAfee, OU = Orion, CN = Orion_CA_epotestsystem
        verify error:num=19:self signed certificate in certificate chain
        ---
        Certificate chain
         0 s:/O=McAfee/OU=Orion/\ **CN=epotestsystem**
           i:/O=McAfee/OU=Orion/CN=Orion_CA_epotestsystem
        -----BEGIN CERTIFICATE-----
        MIIDQTCCAimgAwIBAgIIbIZ7jokCYykwDQYJKoZIhvcNAQEFBQAwPDEPMA0GA1UE
        CgwGTWNBZmVlMQ4wDAYDVQQLDAVPcmlvbjEZMBcGA1UEAwwQT3Jpb25fQ0FfRFhM
        LUVQTzAeFw03MDAxMDEwMDAwMDBaFw00NjA5MDUyMzM3MjVaMDMxDzANBgNVBAoM
        Bk1jQWZlZTEOMAwGA1UECwwFT3Jpb24xEDAOBgNVBAMMB0RYTC1FUE8wggEiMA0G
        CSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCPBctQ4yvubzJlJII4yiFaLbch0dFy
        aUHR6WUJUumAMgHr5Qk06t/I5zFbAvEQYzKsWpX5qPLt90ZwVdEYipTDeuR4zp5c
        AUy8tgPNGGVwdcLraw6du/qw4knOsI9aWzQ0iCXKkthOEAtV+6CPeKVtKfjNi0la
        UsX0s7S3PQzEjppDVojoXAyt0EA0d38mEEoNpt02oJpCldo8JAtLB8GytVkYxxNi
        aSMfb/Ix36PQXZuU7id1xA7y0oT9slBY3Scs4H0vr1FAv4a9ChE7sCOFH9ng+MbM
        kPjBVevcSIsOcZdfs4ACGwiPrp0rWxGl71frJ0qx4RQnWbBq4jRPRNQ7AgMBAAGj
        UDBOMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYEFOnjEeu4L3W6Qyc/r37OJaMi5mfh
        MB8GA1UdIwQYMBaAFKitli7CNwfamTztGieYRrWLs57FMA0GCSqGSIb3DQEBBQUA
        A4IBAQARcMWJnIKC97cqT8ok0w3sEaVhplkI518tnctyoHgcavNRbbNFMjWWybzp
        +zrGCehV7j+IIeVI8Zkxom6CByeAl//J4IeZe8T862ZRvjy9oNeojlmWXlAhSX+2
        8NzATXCvmVzM+qE3F+k1cpD8MFwkIdPY6osOqdPM7Fit04jwizdyg5JFkJPH7aeB
        FzngfaQOcZv+WFfcMNftUIpRlusRsvYdU8TU3mYCi5G5L3Uva4RLsmb3z5m/V+f4
        CGrL15OX6nduGr5D8mfWHXdlxF1KWx7FlCHdgzHws5+w+KIPoDr0u5XK38xxBXIm
        KTyOYAwDg5Mo/2R33q/Fy1fsY8nG
        -----END CERTIFICATE-----
         1 s:/O=McAfee/OU=Orion/CN=Orion_CA_epotestsystem
           i:/O=McAfee/OU=Orion/CN=Orion_CA_epotestsystem
        **-----BEGIN CERTIFICATE-----
        MIIDTTCCAjWgAwIBAgIIffd6gTDU39wwDQYJKoZIhvcNAQEFBQAwPDEPMA0GA1UE
        CgwGTWNBZmVlMQ4wDAYDVQQLDAVPcmlvbjEZMBcGA1UEAwwQT3Jpb25fQ0FfRFhM
        LUVQTzAeFw03MDAxMDEwMDAwMDBaFw00NjA5MDUyMzM3MjRaMDwxDzANBgNVBAoM
        Bk1jQWZlZTEOMAwGA1UECwwFT3Jpb24xGTAXBgNVBAMMEE9yaW9uX0NBX0RYTC1F
        UE8wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDRMqxPEBBkYrcmWg5T
        X2r3Z+bidvGGcPzA2vACvdY4DCGkLTtc085EOQoULRNdGSI6yP9W9YH8nquTreHW
        O80Aj29kr9Il3+JXad04LzBbjW5MhMCf4fnGiJ5E9ud2BE/xc6RTco/8bIoR27BC
        VoTnyHcU0gHz7+PZWaQrPhRKEaNbG3RddY7zKjq56s32rBti2LBbjGg7qVSMLewy
        MuBl9owzWwYC8bJnbqHH3h4LdtsG/Zb1ohsR2PaY2gb+Bn2DjWlBVFiFozRKKSLU
        ipXlBxiYRRrkfOhEneWiptdLo65cXLd09hRc8h7dEPlYl9jZHGpOBvX1aGjre8w8
        LlrXAgMBAAGjUzBRMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFKitli7CNwfa
        mTztGieYRrWLs57FMB8GA1UdIwQYMBaAFKitli7CNwfamTztGieYRrWLs57FMA0G
        CSqGSIb3DQEBBQUAA4IBAQAyHKcG55dOvJJPRf9Xt+Uj3nwd1gyehbOhKJYfDqeZ
        l5EYGuNpX3HFl3BLjNxqxoj/aw1ICJX4AQQpFRsnB2CjQA53/1+0Cmvq4lw7qL/A
        5sbshJKy+4291THE16ynqAF2cySlxhdSpvDMB3Z0v9iGqt5yYvhMc5yHhCpipj0r
        iYY/K8QhEtruGy4lHxjwKOf5Ky1nX1pAZmRK4IDQTdn4iT3Cl9Jgr+ERFou7PHXN
        0k8wmi1b2oPp5OCJoeB4xzsrbdG2aCgTDTflzL9RiEeflhwlWim2X2oCyZKVW4a4
        /Tzcdk4tZlgZazxEDTJ8wI+12JNGBXMN5fuaF5Yuykf1
        -----END CERTIFICATE-----**

        ...

In the output above, the two important portions for validating the ePO server's certificate have been
highlighted in bold.

1. The first portion includes the common name (CN) associated with the ePO server's certificate.

   In this particular example the CN is as follows: ``CN=epotestsystem``

   Based on this, for hostname validation to succeed the ``host`` value for the ePO server as defined in the
   service configuration file must have a value of ``epotestsystem``.

2. The second portion highlighted is the certificate of the CA that was used to sign the ePO server's certificate.

   For certificate validation to succeed, this certificate text must be copied (including the `BEGIN` and `END` lines)
   into a new file. Next, the ``verifyCertBundle`` value for the ePO server as defined in the service configuration
   file must have a path to this newly created file.

   For example:

    .. parsed-literal::

        -----BEGIN CERTIFICATE-----
        MIIDTTCCAjWgAwIBAgIIffd6gTDU39wwDQYJKoZIhvcNAQEFBQAwPDEPMA0GA1UE
        CgwGTWNBZmVlMQ4wDAYDVQQLDAVPcmlvbjEZMBcGA1UEAwwQT3Jpb25fQ0FfRFhM
        LUVQTzAeFw03MDAxMDEwMDAwMDBaFw00NjA5MDUyMzM3MjRaMDwxDzANBgNVBAoM
        Bk1jQWZlZTEOMAwGA1UECwwFT3Jpb24xGTAXBgNVBAMMEE9yaW9uX0NBX0RYTC1F
        UE8wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDRMqxPEBBkYrcmWg5T
        X2r3Z+bidvGGcPzA2vACvdY4DCGkLTtc085EOQoULRNdGSI6yP9W9YH8nquTreHW
        O80Aj29kr9Il3+JXad04LzBbjW5MhMCf4fnGiJ5E9ud2BE/xc6RTco/8bIoR27BC
        VoTnyHcU0gHz7+PZWaQrPhRKEaNbG3RddY7zKjq56s32rBti2LBbjGg7qVSMLewy
        MuBl9owzWwYC8bJnbqHH3h4LdtsG/Zb1ohsR2PaY2gb+Bn2DjWlBVFiFozRKKSLU
        ipXlBxiYRRrkfOhEneWiptdLo65cXLd09hRc8h7dEPlYl9jZHGpOBvX1aGjre8w8
        LlrXAgMBAAGjUzBRMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFKitli7CNwfa
        mTztGieYRrWLs57FMB8GA1UdIwQYMBaAFKitli7CNwfamTztGieYRrWLs57FMA0G
        CSqGSIb3DQEBBQUAA4IBAQAyHKcG55dOvJJPRf9Xt+Uj3nwd1gyehbOhKJYfDqeZ
        l5EYGuNpX3HFl3BLjNxqxoj/aw1ICJX4AQQpFRsnB2CjQA53/1+0Cmvq4lw7qL/A
        5sbshJKy+4291THE16ynqAF2cySlxhdSpvDMB3Z0v9iGqt5yYvhMc5yHhCpipj0r
        iYY/K8QhEtruGy4lHxjwKOf5Ky1nX1pAZmRK4IDQTdn4iT3Cl9Jgr+ERFou7PHXN
        0k8wmi1b2oPp5OCJoeB4xzsrbdG2aCgTDTflzL9RiEeflhwlWim2X2oCyZKVW4a4
        /Tzcdk4tZlgZazxEDTJ8wI+12JNGBXMN5fuaF5Yuykf1
        -----END CERTIFICATE-----
