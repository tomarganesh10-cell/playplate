# DNS Configuration — `trading.playplate.in` (Hostinger)

This guide configures the `trading` subdomain to point at your Hostinger VPS.

## What you need

- Your VPS public IPv4 address (Hostinger panel → VPS → Overview, e.g. `203.0.113.45`).
- Access to DNS management for `playplate.in`. If the domain's nameservers are
  Hostinger's, manage records in **hPanel → Domains → playplate.in → DNS / Nameservers**.

## Required records

Create the subdomain `trading` as an **A record** pointing to the VPS IP.

| Type  | Name (Host) | Value / Points to     | TTL   |
|-------|-------------|-----------------------|-------|
| A     | `trading`   | `<YOUR_VPS_IPV4>`     | 300   |
| AAAA  | `trading`   | `<YOUR_VPS_IPV6>` *(optional, if your VPS has IPv6)* | 300 |

> In Hostinger's DNS editor, **Name** is just the subdomain label `trading`
> (not the full `trading.playplate.in`). The zone appends the domain for you.

If you instead want the apex/root to redirect, that is separate; this project
only requires the `trading` subdomain.

### Optional CAA record (recommended)

Restrict which CAs may issue certificates for your domain (allows Let's Encrypt):

| Type | Name | Value                         | TTL |
|------|------|-------------------------------|-----|
| CAA  | `@`  | `0 issue "letsencrypt.org"`   | 300 |

## Step-by-step (Hostinger hPanel)

1. Log in to Hostinger → **Domains** → select `playplate.in`.
2. Open **DNS / Nameservers**.
3. Under **Manage DNS records**, choose **Add record**.
4. Type: `A`. Name: `trading`. Points to: your VPS IPv4. TTL: `300`. **Add**.
5. (Optional) Repeat for `AAAA` and `CAA` as above.
6. If an existing `trading` record points elsewhere, edit/delete it first.

## Verify propagation

DNS can take from a few minutes up to a couple of hours. Verify with:

```bash
dig +short trading.playplate.in            # should print your VPS IP
nslookup trading.playplate.in
# Or use an online checker like dnschecker.org for global propagation.
```

Once `dig` returns the correct IP from your VPS and locally, proceed to
[`SSL_CONFIGURATION.md`](SSL_CONFIGURATION.md) to issue the certificate.

## Troubleshooting

- **Wrong/old IP returned:** you edited the wrong zone or TTL hasn't expired.
  Wait for the TTL, then re-check.
- **Using Cloudflare or external DNS?** Create the same A record there, and if
  proxying (orange cloud), either disable proxy for the ACME HTTP-01 challenge
  or switch to DNS-01. The bundled `init_ssl.sh` uses HTTP-01.
- **`NXDOMAIN`:** the record name is wrong (use `trading`, not the full FQDN).
