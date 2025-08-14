# app/templates/email_templates.py

def pago_realizado_template(pago):
    return f"""
    <html>
      <body>
        <h2>Se ha realizado un nuevo pago</h2>
        <ul>
          <li><b>Monto:</b> {pago.txtMontoPagar}</li>
          <li><b>Forma de pago:</b> {pago.txtFormaPago}</li>
          <li><b>Fecha:</b> {pago.dFechaPago}</li>
          <li><b>Usuario:</b> {pago.txtUsuarioPaga}</li>
        </ul>
        <p>Revisar en el sistema para más detalles.</p>
      </body>
    </html>
    """
