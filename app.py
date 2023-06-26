from datetime import datetime
from flask import Flask, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)
app.config.from_pyfile("config.py")

from models import db 
from models import Preceptor, Curso, Estudiante, Asistencia, Padre

class estadoEstudiante:
    estudiante: Estudiante
    asist_Aula: int
    asist_EduFisi: int
    aus_justi_Aula: int
    aus_sinjusti_Aula: int
    aus_justi_EduFisi: int
    aus_sinjusti_EduFisi: int
    total_aus: int

    def __init__(self, estudiante, asist_Aula, asist_EduFisi, aus_justi_Aula, aus_sinjusti_Aula, aus_justi_EduFisi, aus_sinjusti_EduFisi, total_aus):
        self.estudiante = estudiante               
        self.asist_Aula = asist_Aula                        #cont1
        self.asist_EduFisi = asist_EduFisi                  #cont2
        self.aus_justi_Aula = aus_justi_Aula                #cont3
        self.aus_sinjusti_Aula = aus_sinjusti_Aula          #cont4
        self.aus_justi_EduFisi = aus_justi_EduFisi          #cont5
        self.aus_sinjusti_EduFisi = aus_sinjusti_EduFisi    #cont6
        self.total_aus = total_aus                          #cont7


@app.route("/")
def inicio():
    return render_template("inicio.html")



@app.route("/acceder", methods = ["GET", "POST"])
def acceder():
    if request.method == "POST":
        if not request.form["email"] or not request.form["password"]:
            return render_template("error.html", error="Por favor ingrese los datos requeridos")
        else:
            if request.form["rol"] == "preceptor":
                usuario = Preceptor.query.filter_by(correo = request.form["email"]).first()
                return analizarDatos(usuario,"preceptor")
            elif request.form["rol"] == "padre":
                usuario = Padre.query.filter_by(correo = request.form["email"]).first()
                return analizarDatos(usuario,"padre")
            else:
                return render_template("error.html", error="Rol INVALIDO")
    else:
        return render_template("acceder.html")
    

        
                
def analizarDatos(usuario,rol):
    if usuario is None:
        return render_template("error.html", error="Usuario no encontrado")
    else:
        verificacion = (hashlib.md5(bytes(request.form["password"], encoding="utf-8")).hexdigest()) == usuario.clave
        if verificacion:
            if rol == "preceptor":
                session["usuarioID"] = usuario.id
                return render_template("menuPreceptor.html", usuario = usuario)
            else:
                return render_template("error.html", error="Bienvenido Sr/a Padre/Madre")      
        else:
            return render_template("error.html", error="Contraseña invalida")



@app.route("/registrarAsistencia", methods=["GET", "POST"])
def registrarAsistencia():
    if request.method == "POST":
        if not request.form["fecha"] or not request.form["cursoID"] or not request.form["asistencia"]:
            return render_template("error.html", error="Necesita introducir todos los datos")  
        else:
            fecha = request.form["fecha"]
            fecha = datetime.strptime(fecha, '%Y-%m-%d') #convierte el string fecha en formato fecha de python
            fecha = fecha.strftime('%d-%m-%Y') #convierte el formato fecha de python a un string con el formato que voy a almacenar
            estudiantes = Estudiante.query.filter_by(idcurso = request.form["cursoID"]).all()
            datos = {
            "estudiantes":estudiantes,
            "aula": request.form["clase"],
            "fecha": fecha
            }
            return render_template("listarAlumnos.html", datos=datos)
    else:    
        usuarioID = session.get("usuarioID")
        usuario = Preceptor.query.get(usuarioID)
        cursos = Curso.query.filter_by(idpreceptor=usuario.id).all()
        esRegistroAsistencia = True
        return render_template("listaDeCursos.html", cursos = cursos, usuario = usuario, esRegistroAsistencia = esRegistroAsistencia)



@app.route("/registrarDatos", methods=["GET", "POST"])
def registrarDatos():
    fecha = request.form["fecha"]
    clase = request.form["aula"]
    IDestudiantes = request.form.getlist("IDestudiante")
    justificaciones = request.form.getlist("justificacion")
    asistencias = request.form.getlist("asistencia")
    for i in range(len(IDestudiantes)):
        justificacion = justificaciones[i]
        asistencia = asistencias[i]
        IDestudiante = IDestudiantes[i]
        nuevaAsistencia= Asistencia(fecha = fecha, codigoclase = clase, asistio = asistencia, justificacion=justificacion, idestudiante = IDestudiante)
        db.session.add(nuevaAsistencia)
        db.session.commit()
    return render_template("error.html", error="SE REGISTRARON LOS DATOS")



@app.route("/informeDetallado", methods=["GET", "POST"])
def informeDetallado():
    cont1 = cont2 = cont3 = cont4 = cont5 = cont6 = cont7 = 0
    listaEstados = []
    if request.method == "POST":
        cursoID = request.form["cursoID"]
        estudiantes = Estudiante.query.filter_by(idcurso=cursoID).all()
        for estudiante in estudiantes:
            asistencias = Asistencia.query.filter_by(idestudiante = estudiante.id)
            for asistencia in asistencias:
                match(asistencia.asistio):
                    case "s":
                        if asistencia.codigoclase ==1:#aula
                            cont1 +=1
                        else:#edu fisica
                            cont2 +=1
                    case "n":
                        if asistencia.codigoclase ==1:#aula
                            if asistencia.justificacion != "":#AULA justificada
                                cont3 +=1
                                cont7 +=1
                            else:#AULA sin justificar
                                cont4 +=1
                                cont7 +=1
                        else:#edu fisica
                            if asistencia.justificacion != "":#EDU FISICA justificada
                                cont5 +=1
                                cont7 +=0.5
                            else:#EDU FISICA sin justificar
                                cont7 +=0.5
                                cont6 +=1
            listaEstados.append(estadoEstudiante(estudiante,cont1,cont2,cont3,cont4,cont5,cont6,cont7))
        return render_template("listaDetallada.html", lista=listaEstados)        
    else:
        usuarioID = session.get("usuarioID")
        usuario = Preceptor.query.get(usuarioID)
        cursos = Curso.query.filter_by(idpreceptor=usuario.id).all()
        esRegistroAsistencia = False
        return render_template("listaDeCursos.html", cursos = cursos, usuario = usuario, esRegistroAsistencia = esRegistroAsistencia)



if __name__ == '__main__':
    with app.app_context():
        app.run(debug = True)
        db.create_all()

	