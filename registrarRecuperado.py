"""@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        if not request.form['nombre'] or not request.form['apellido'] or not request.form['password']:
            return render_template("error.html", error="Por favor ingrese los datos requeridos")
        else:
            if request.form["rol"] == "preceptor":
                nuevoUsuario= Preceptor(nombre = request.form["nombre"], apellido = request.form['apellido'], correo = request.form["email"], clave = request.form["password"])    
                db.session.add(nuevoUsuario)
                db.session.commit()
                return render_template("inicio.html")
            else:
                nuevoUsuario= Padre(nombre = request.form["nombre"], apellido = request.form['apellido'], correo = request.form["email"], clave = request.form["password"])    
                db.session.add(nuevoUsuario)
                db.session.commit()
                return render_template("inicio.html")
    else:
        return render_template("registro.html")"""