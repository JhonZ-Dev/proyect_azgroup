const ip = '172.16.10.38';

//172.16.10.37
//192.168.18.12
const port = 5050;


export const api_login = {
  production: false,
  ip,
  port,
  apiUrl: `http://${ip}:${port}/`
};

export const api_items = {
  production: false,
  ip,
  port,
  apiUrl: `http://${ip}:${port}/items/`
}

export const api_informacion = {
  production: false,
  ip,
  port,
  apiUrl: `http://${ip}:${port}/informaciones/`
}

export const api_exportToWord={
  production: false,
  ip,
  port,
  apiUrl: `http://${ip}:${port}/informaciones/`
}

export const api_pagos={
  production: false,
  ip,
  port,
  apiUrlPagos: `http://${ip}:${port}/pagos/`
}
