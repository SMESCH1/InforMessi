#!/usr/bin/env python3
"""Batch: agrega eventos, limpia junk, corrige datos."""
import json

with open('data/events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Fix Cuti Romero wrong date
data['events'] = [e for e in data['events'] if not (e.get('person') == 'Cuti Romero' and e.get('date') == '1997-10-08')]

# 2. Remove messy 2026-dated historical events (scraped Wikipedia junk)
before = len(data['events'])
data['events'] = [e for e in data['events']
    if not (e.get('date', '').startswith('2026-') and e.get('type') == 'historical')]
removed_junk = before - len(data['events'])

# 3. Remove duplicate Messi birthday (2024-01-01 wrong date)
data['events'] = [e for e in data['events']
    if not (e.get('date') == '2024-01-01' and e.get('person') == 'Lionel Messi' and e.get('type') == 'birthday')]

new_events = [
    # === MARZO ===
    {"date": "1980-03-21", "type": "birthday", "priority": "medium", "person": "Ronaldinho", "age": 46, "description": "Cumplea\u00f1os de Ronaldinho Ga\u00facho. Leyenda brasile\u00f1a, Bal\u00f3n de Oro 2005, campe\u00f3n del mundo 2002."},
    {"date": "1961-03-21", "type": "birthday", "priority": "medium", "person": "Lothar Matth\u00e4us", "age": 65, "description": "Cumplea\u00f1os de Lothar Matth\u00e4us. Campe\u00f3n del mundo 1990, primer FIFA World Player. Disput\u00f3 5 Mundiales."},
    {"date": "1991-03-21", "type": "birthday", "priority": "low", "person": "Antoine Griezmann", "age": 35, "description": "Cumplea\u00f1os de Antoine Griezmann. Campe\u00f3n del mundo 2018 con Francia, estrella del Atl\u00e9tico Madrid."},
    {"date": "1947-03-24", "type": "birthday", "priority": "medium", "person": "Archie Gemmill", "age": 79, "description": "Cumplea\u00f1os de Archie Gemmill. Autor del golazo a Holanda en el Mundial 1978 disputado en Argentina."},
    {"date": "2000-03-26", "type": "birthday", "priority": "low", "person": "Fausto Vera", "age": 26, "description": "Cumplea\u00f1os de Fausto Vera. Mediocampista argentino, selecci\u00f3n juvenil."},
    {"date": "1968-03-31", "type": "birthday", "priority": "low", "person": "C\u00e9sar Sampaio", "age": 58, "description": "Cumplea\u00f1os de C\u00e9sar Sampaio. Autor del primer gol del Mundial 1998 (Brasil vs Escocia, partido inaugural)."},
    # === ABRIL ===
    {"date": "1990-04-02", "type": "birthday", "priority": "low", "person": "Miralem Pjani\u0107", "age": 36, "description": "Cumplea\u00f1os de Miralem Pjani\u0107. Mediocampista bosnio, maestro del tiro libre en Juventus y Barcelona."},
    {"date": "1976-04-05", "type": "birthday", "priority": "low", "person": "Fernando Morientes", "age": 50, "description": "Cumplea\u00f1os de Fernando Morientes. Delantero espa\u00f1ol, gan\u00f3 tres Champions League con Real Madrid."},
    {"date": "1967-04-07", "type": "birthday", "priority": "high", "person": "Bodo Illgner", "age": 59, "description": "Cumplea\u00f1os de Bodo Illgner. Arquero alem\u00e1n campe\u00f3n del mundo 1990 en la final contra Argentina (1-0)."},
    {"date": "1983-04-07", "type": "birthday", "priority": "low", "person": "Franck Rib\u00e9ry", "age": 43, "description": "Cumplea\u00f1os de Franck Rib\u00e9ry. Leyenda del Bayern M\u00fanich, finalista del Mundial 2006 con Francia."},
    {"date": "1950-04-08", "type": "birthday", "priority": "medium", "person": "Grzegorz Lato", "age": 76, "description": "Cumplea\u00f1os de Grzegorz Lato. Bota de Oro del Mundial 1974 con 7 goles, leyenda del f\u00fatbol polaco."},
    {"date": "1996-04-09", "type": "birthday", "priority": "high", "person": "Giovani Lo Celso", "age": 30, "description": "Cumplea\u00f1os de Giovani Lo Celso. Mediocampista campe\u00f3n del mundo en Qatar 2022 con la Selecci\u00f3n Argentina."},
    {"date": "1973-04-10", "type": "birthday", "priority": "medium", "person": "Roberto Carlos", "age": 53, "description": "Cumplea\u00f1os de Roberto Carlos. Legendario lateral brasile\u00f1o, campe\u00f3n del mundo 2002, famoso por su tiro libre imposible."},
    {"date": "1991-04-11", "type": "birthday", "priority": "low", "person": "Thiago Alc\u00e1ntara", "age": 35, "description": "Cumplea\u00f1os de Thiago Alc\u00e1ntara. Mediocampista espa\u00f1ol hijo de Mazinho, campe\u00f3n de Champions con Barcelona y Bayern."},
    {"date": "1941-04-12", "type": "birthday", "priority": "medium", "person": "Bobby Moore", "age": 85, "description": "Cumplea\u00f1os de Bobby Moore. Capit\u00e1n de Inglaterra campe\u00f3n del mundo 1966, uno de los mejores defensores de la historia."},
    {"date": "1960-04-13", "type": "birthday", "priority": "high", "person": "Rudi V\u00f6ller", "age": 66, "description": "Cumplea\u00f1os de Rudi V\u00f6ller. Delantero alem\u00e1n que disput\u00f3 dos finales mundialistas contra Argentina (1986 y 1990)."},
    {"date": "1978-04-13", "type": "birthday", "priority": "medium", "person": "Carles Puyol", "age": 48, "description": "Cumplea\u00f1os de Carles Puyol. Capit\u00e1n del Barcelona, campe\u00f3n del mundo 2010, gol de cabeza hist\u00f3rico en semifinal vs Alemania."},
    {"date": "1999-04-14", "type": "birthday", "priority": "low", "person": "Matteo Guendouzi", "age": 27, "description": "Cumplea\u00f1os de Matteo Guendouzi. Mediocampista franc\u00e9s, subcampe\u00f3n del mundo en Qatar 2022 ante Argentina."},
    {"date": "1989-04-15", "type": "historical", "priority": "high", "person": "N/A", "description": "Tragedia de Hillsborough: 97 hinchas de Liverpool mueren durante semifinal de FA Cup. Cambi\u00f3 la seguridad en estadios para siempre."},
    {"date": "2003-04-15", "type": "birthday", "priority": "low", "person": "Mat\u00edas Soul\u00e9", "age": 23, "description": "Cumplea\u00f1os de Mat\u00edas Soul\u00e9. Mediapunta argentino de la Roma, joven promesa del f\u00fatbol argentino."},
    {"date": "1977-04-16", "type": "birthday", "priority": "low", "person": "Freddie Ljungberg", "age": 49, "description": "Cumplea\u00f1os de Freddie Ljungberg. Extremo sueco del Arsenal de los Invencibles, disput\u00f3 2 Mundiales."},
    {"date": "1989-04-17", "type": "birthday", "priority": "low", "person": "Charles Ar\u00e1nguiz", "age": 37, "description": "Cumplea\u00f1os de Charles Ar\u00e1nguiz. Mediocampista chileno, bicampe\u00f3n de Copa Am\u00e9rica 2015 y 2016 ante Argentina."},
    {"date": "1996-04-18", "type": "birthday", "priority": "low", "person": "Denzel Dumfries", "age": 30, "description": "Cumplea\u00f1os de Denzel Dumfries. Lateral holand\u00e9s del Inter de Mil\u00e1n, goleador en el Mundial 2022."},
    {"date": "2003-04-21", "type": "birthday", "priority": "low", "person": "Xavi Simons", "age": 23, "description": "Cumplea\u00f1os de Xavi Simons. Joven estrella holandesa, figura en la Euro 2024, formado en Barcelona y PSG."},
    {"date": "1982-04-22", "type": "birthday", "priority": "high", "person": "Kak\u00e1", "age": 44, "description": "Cumplea\u00f1os de Kak\u00e1. Genio brasile\u00f1o, Bal\u00f3n de Oro 2007, campe\u00f3n del mundo 2002, Champions League con Milan 2007."},
    {"date": "1982-04-23", "type": "birthday", "priority": "low", "person": "Kyle Beckerman", "age": 44, "description": "Cumplea\u00f1os de Kyle Beckerman. Mediocampista estadounidense, 58 selecciones con EEUU, pa\u00eds sede del Mundial 2026."},
    {"date": "1987-04-24", "type": "birthday", "priority": "low", "person": "Jan Vertonghen", "age": 39, "description": "Cumplea\u00f1os de Jan Vertonghen. Defensor belga, m\u00e1s de 150 caps con B\u00e9lgica, finalista Champions 2019 con Tottenham."},
    {"date": "1998-04-27", "type": "birthday", "priority": "high", "person": "Cuti Romero", "age": 28, "description": "Cumplea\u00f1os de Cristian 'Cuti' Romero. Defensor campe\u00f3n del mundo en Qatar 2022, titular indiscutible de la Scaloneta."},
    {"date": "1999-04-29", "type": "birthday", "priority": "low", "person": "Mateo Retegui", "age": 27, "description": "Cumplea\u00f1os de Mateo Retegui. Nacido en Argentina, delantero de la selecci\u00f3n de Italia. Hijo de Carlos Retegui, leyenda del hockey argentino."},
    {"date": "1992-04-30", "type": "birthday", "priority": "low", "person": "Marc-Andr\u00e9 ter Stegen", "age": 34, "description": "Cumplea\u00f1os de ter Stegen. Arquero alem\u00e1n del Barcelona, pilar del club durante m\u00e1s de una d\u00e9cada."},
    # === MAYO ===
    {"date": "1975-05-02", "type": "birthday", "priority": "medium", "person": "David Beckham", "age": 51, "description": "Cumplea\u00f1os de David Beckham. Leyenda inglesa (Manchester United, Real Madrid), \u00edcono mundial del f\u00fatbol."},
    {"date": "1985-05-03", "type": "birthday", "priority": "high", "person": "Ezequiel Lavezzi", "age": 41, "description": "Cumplea\u00f1os del 'Pocho' Lavezzi. Delantero argentino de Napoli y PSG, figura de la Selecci\u00f3n en el Mundial 2014."},
    {"date": "1973-05-04", "type": "birthday", "priority": "medium", "person": "Guillermo Barros Schelotto", "age": 53, "description": "Cumplea\u00f1os de Guillermo Barros Schelotto. \u00cddolo de Boca Juniors, m\u00faltiples t\u00edtulos incluyendo Copa Libertadores."},
    {"date": "2024-05-05", "type": "death", "priority": "high", "person": "C\u00e9sar Luis Menotti", "description": "Aniversario del fallecimiento de C\u00e9sar Luis Menotti, DT campe\u00f3n del mundo con Argentina en 1978."},
    {"date": "1976-05-05", "type": "birthday", "priority": "medium", "person": "Juan Pablo Sor\u00edn", "age": 50, "description": "Cumplea\u00f1os de Juan Pablo Sor\u00edn. Lateral ic\u00f3nico de la Selecci\u00f3n Argentina, mundialista en 2002 y 2006."},
    {"date": "1983-05-06", "type": "birthday", "priority": "low", "person": "Dani Alves", "age": 43, "description": "Cumplea\u00f1os de Dani Alves. El jugador con m\u00e1s t\u00edtulos en la historia del f\u00fatbol profesional."},
    {"date": "1965-05-07", "type": "birthday", "priority": "medium", "person": "Norman Whiteside", "age": 61, "description": "Cumplea\u00f1os de Norman Whiteside. Jugador m\u00e1s joven en disputar un Mundial (17 a\u00f1os y 41 d\u00edas, Espa\u00f1a 1982)."},
    {"date": "1960-05-08", "type": "birthday", "priority": "high", "person": "Franco Baresi", "age": 66, "description": "Cumplea\u00f1os de Franco Baresi. Legendario defensor del AC Milan, considerado uno de los mejores de la historia."},
    {"date": "1966-05-08", "type": "birthday", "priority": "medium", "person": "Cl\u00e1udio Taffarel", "age": 60, "description": "Cumplea\u00f1os de Taffarel. Arquero brasile\u00f1o campe\u00f3n del mundo 1994 y subcampe\u00f3n 1998."},
    {"date": "1984-05-11", "type": "birthday", "priority": "high", "person": "Andr\u00e9s Iniesta", "age": 42, "description": "Cumplea\u00f1os de Andr\u00e9s Iniesta. Leyenda del Barcelona, autor del gol que dio el Mundial 2010 a Espa\u00f1a vs Holanda."},
    {"date": "1988-05-12", "type": "birthday", "priority": "medium", "person": "Marcelo Vieira", "age": 38, "description": "Cumplea\u00f1os de Marcelo. Lateral legendario del Real Madrid, gan\u00f3 cuatro Champions League."},
    {"date": "1901-05-15", "type": "birthday", "priority": "high", "person": "Luis Monti", "age": 125, "description": "Cumplea\u00f1os de Luis Monti. \u00danico jugador en disputar finales de Mundial con dos selecciones: Argentina 1930 e Italia 1934 (campe\u00f3n)."},
    {"date": "1977-05-17", "type": "birthday", "priority": "low", "person": "Luca Toni", "age": 49, "description": "Cumplea\u00f1os de Luca Toni. Delantero italiano campe\u00f3n del mundo 2006, Bota de Oro de la Bundesliga."},
    {"date": "1904-05-21", "type": "historical", "priority": "high", "person": "N/A", "description": "Fundaci\u00f3n de la FIFA en Par\u00eds. D\u00eda hist\u00f3rico que sent\u00f3 las bases del f\u00fatbol organizado a nivel mundial."},
    {"date": "1986-05-21", "type": "birthday", "priority": "low", "person": "Mario Mand\u017euki\u0107", "age": 40, "description": "Cumplea\u00f1os de Mario Mand\u017euki\u0107. Delantero croata, gol en la final del Mundial 2018 contra Francia."},
    {"date": "1946-05-22", "type": "birthday", "priority": "medium", "person": "George Best", "age": 80, "description": "Cumplea\u00f1os de George Best. Bal\u00f3n de Oro 1968 con Manchester United, uno de los m\u00e1s grandes de la historia."},
    {"date": "1987-05-22", "type": "birthday", "priority": "low", "person": "Arturo Vidal", "age": 39, "description": "Cumplea\u00f1os de Arturo Vidal. Mediocampista chileno, bicampe\u00f3n de Copa Am\u00e9rica 2015 y 2016 ante Argentina."},
    {"date": "1961-05-23", "type": "birthday", "priority": "low", "person": "Daniele Massaro", "age": 65, "description": "Cumplea\u00f1os de Daniele Massaro. Autor de 2 goles en la final de Champions 1994 (Milan 4-0 Barcelona)."},
    {"date": "1909-05-26", "type": "birthday", "priority": "low", "person": "Matt Busby", "age": 117, "description": "Cumplea\u00f1os de Matt Busby. Creador de los 'Busby Babes' del Manchester United, sobreviviente de M\u00fanich 1958."},
    {"date": "1970-05-29", "type": "birthday", "priority": "low", "person": "Roberto Di Matteo", "age": 56, "description": "Cumplea\u00f1os de Roberto Di Matteo. Como DT del Chelsea gan\u00f3 la Champions League 2012 en el milagro de M\u00fanich."},
    {"date": "1989-05-31", "type": "birthday", "priority": "low", "person": "Marco Reus", "age": 37, "description": "Cumplea\u00f1os de Marco Reus. Leyenda del Borussia Dortmund, m\u00e1ximo referente del club durante una d\u00e9cada."},
    # === JUNIO ===
    {"date": "1970-06-07", "type": "birthday", "priority": "medium", "person": "Caf\u00fa", "age": 56, "description": "Cumplea\u00f1os de Caf\u00fa. Bicampe\u00f3n del mundo con Brasil (1994 y 2002), r\u00e9cord de partidos con la selecci\u00f3n brasile\u00f1a."},
    # === CONVOCADOS EXTRA (profundidad) ===
    {"date": "2003-04-28", "type": "birthday", "priority": "low", "person": "Tom\u00e1s Palacios", "age": 23, "description": "Cumplea\u00f1os de Tom\u00e1s Palacios. Defensor de la Selecci\u00f3n Argentina, 1.96m, a pr\u00e9stamo del Inter en Estudiantes."},
    {"date": "1997-05-10", "type": "birthday", "priority": "low", "person": "Marcos Senesi", "age": 29, "description": "Cumplea\u00f1os de Marcos Senesi. Defensor zurdo de Bournemouth, convocado a la Selecci\u00f3n Argentina."},
]

data['events'].extend(new_events)

with open('data/events.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'OK - {len(data["events"])} eventos')
print(f'Wikipedia junk eliminado: {removed_junk}')
print(f'Nuevos eventos agregados: {len(new_events)}')
