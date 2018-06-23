import cairocffi as cairo
import math
from main import Application

class Chart_Img():

    MAX_HEIGHT = 25000
    WIDTH = 1024
    MEASURE_OFFSET = 40
    LINE_OFFSET = 125
    EPSILON = 0.001
    NOTE_RADIUS = 3
    STAR_SCALE = 30

    STAR_POINTS = ( 
        ( 0, 85 ), 
        ( 75, 75 ), 
        ( 100, 10 ), 
        ( 125, 75 ), 
        ( 200, 85 ),
        ( 150, 125 ), 
        ( 160, 190 ),
        ( 100, 150 ), 
        ( 40, 190 ),
        ( 50, 125 ),
        ( 0, 85 )
    )

    COLORS = [
        [0, 0.9, 0], 
        [1, 0, 0], 
        [1, 1, 0],
        [0, 0.3, 1],
        [1, 0.7, 0],
        [1, 0, 1],
        [0, 0.7, 0]
    ]

    def __init__(self, song, chart):
        self.song = song
        self.chart = chart
        self.c_y = 0

        self.notes = self.chart.notes

        self.chart_length = self.notes[len(self.notes) - 1]["position"] + \
        self.notes[len(self.notes) - 1]["length"]

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2

        self.m2l = self.line_length / (self.song.resolution * 24)

        height = self.calculate_height()

        if height > self.MAX_HEIGHT:
            height = self.MAX_HEIGHT

        self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, height)
        self.cr = cairo.Context(self.ims)

        self.cr.set_source_rgb(1, 1, 1)
        self.cr.rectangle(0, 0, self.WIDTH, height)
        self.cr.fill()

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

        self.c_y += 30

        str_charter = "Charter: " + self.song.charter
        self.cr.set_font_size(12)
        (_, _, width, _, _, _) = self.cr.text_extents(str_charter)
        self.cr.move_to(self.MEASURE_OFFSET / 4, self.c_y)    
        self.cr.show_text(str_charter)

        self.cr.set_font_size(18)
        (_, _, width, _, _, _) = self.cr.text_extents(self.song.name)
        self.cr.move_to(self.WIDTH / 2 - width / 2, self.c_y)    
        self.cr.show_text(self.song.name)

        self.c_y += 20

        self.cr.set_font_size(12) 
        (_, _, width, _, _, _) = self.cr.text_extents(song.DIFFICULTIES[chart.difficulty])
        self.cr.move_to(self.WIDTH / 2 - width / 2, self.c_y)   
        self.cr.show_text(song.DIFFICULTIES[chart.difficulty])

        est_score = "Est. Score: " + str(math.floor(self.chart.base_score(song.time_signatures, True)))
        (_, _, width, _, _, _) = self.cr.text_extents(est_score)
        self.cr.move_to(self.WIDTH - width - self.MEASURE_OFFSET / 4, self.c_y)   
        self.cr.show_text(est_score)

        self.c_y += 60

        self.draw_chart(False)
        self.draw_chart(True)

        self.ims.write_to_png("Chart Images/" + self.song.name.lower().replace(" ", "") + ".png")



    def calculate_height(self):
        height = 110

        c_ts = 0
        self.c_measure_length = 0
        c_length = 0
        self.c_x = self.MEASURE_OFFSET      
        

        while c_length <= self.chart_length:
            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length:
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"] 

            if (self.c_measure_length + measure_length) * self.m2l > self.line_length:
                self.c_x = self.MEASURE_OFFSET
                height += self.LINE_OFFSET
                self.c_measure_length = 0

            self.c_x += measure_length * self.m2l
            c_length += measure_length
            self.c_measure_length += measure_length

        return height + self.LINE_OFFSET * 3

    def draw_note(self, x, y, color, star):
        
        if color == 7:
            color = 5

        self.cr.set_source_rgb(0.7, 0.7, 0.7)

        if star:
            if color == 5:
                for i in range(10):
                    self.cr.line_to(self.STAR_POINTS[i][0] / (self.STAR_SCALE + 5) + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / (self.STAR_SCALE + 5) + y - self.NOTE_RADIUS - 2 * self.notes_offset)   
                self.cr.stroke_preserve()    
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1], 
                self.COLORS[color][2])
                self.cr.fill()

                self.cr.set_source_rgb(0.7, 0.7, 0.7)
                for i in range(10):
                    self.cr.line_to(self.STAR_POINTS[i][0] / (self.STAR_SCALE + 5) + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / (self.STAR_SCALE + 5) + y - self.NOTE_RADIUS + 2 * self.notes_offset)  
                self.cr.stroke_preserve()      
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1], 
                self.COLORS[color][2])
                self.cr.fill()

                self.cr.rectangle(x - (self.NOTE_RADIUS - self.NOTE_RADIUS / 3), 
                y - 2 * self.notes_offset, self.NOTE_RADIUS + self.NOTE_RADIUS / 3, 4 * self.notes_offset)
            else:
                for i in range(10):
                    self.cr.line_to(self.STAR_POINTS[i][0] / self.STAR_SCALE + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / self.STAR_SCALE + y - self.NOTE_RADIUS)   
                self.cr.stroke_preserve()      
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1], 
                self.COLORS[color][2])
        else:
            if color == 5:          
                self.cr.arc(x, y - 2 * self.notes_offset, 
                self.NOTE_RADIUS - self.NOTE_RADIUS / 3, 0, 2 * math.pi)
                self.cr.stroke_preserve()
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1],
                 self.COLORS[color][2])
                self.cr.fill()

                self.cr.set_source_rgb(0.7, 0.7, 0.7)
                self.cr.arc(x, y + 2 * self.notes_offset, 
                self.NOTE_RADIUS - self.NOTE_RADIUS / 3, 0, 2 * math.pi)
                self.cr.stroke_preserve()
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1], 
                self.COLORS[color][2])
                self.cr.fill()
                
                self.cr.rectangle(x - (self.NOTE_RADIUS - self.NOTE_RADIUS / 3), 
                y - 2 * self.notes_offset, self.NOTE_RADIUS + self.NOTE_RADIUS / 3, 4 * self.notes_offset)
            else:
                self.cr.arc(x, y, self.NOTE_RADIUS, 0, 2 * math.pi)
                self.cr.stroke_preserve()      
                self.cr.set_source_rgb(self.COLORS[color][0], self.COLORS[color][1], 
                self.COLORS[color][2])

        self.cr.fill()

    def draw_vert_line(self, color, x):
        self.cr.set_source_rgb(color, color, color)
        self.cr.move_to(x, self.c_y)
        self.cr.line_to(x, self.c_y + self.notes_offset * 4) 
        self.cr.stroke()

    def draw_chart(self, draw_notes): 

        c_length = 0
        #c_bpm = 0
        c_ts = -1
        self.c_measure_length = 0
        self.c_x = self.MEASURE_OFFSET
        self.c_y = 110

        self.notes_offset = 15
        measure_num_offset = 5

        measure_num = 0
        self.line_num = 0

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2
        self.line_lengths = []

        show_ts = False

        n = 0
        note_lengths = [0, 0, 0, 0, 0, 0]

        sp_phrases = self.chart.sp_phrases
        sp = 0
        sp_phrase_length = 0

        bpms = self.song.bpms
        b = 0

        sections = self.song.sections
        s = 0

        self.cr.set_line_width(2)

        while c_length <= self.chart_length:

            measure_num += 1  

            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length: 
                    show_ts = True
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"]    

            if (self.c_measure_length + measure_length) * self.m2l - self.line_length > self.EPSILON:  
                self.line_lengths.append(self.c_measure_length * self.m2l)
                
                if not draw_notes:
                    self.draw_vert_line(0.7, self.c_x)

                self.c_x = self.MEASURE_OFFSET
                self.c_y += self.LINE_OFFSET
                self.c_measure_length = 0

                self.line_num += 1

            if show_ts and not draw_notes:
                self.cr.select_font_face("Arial Black", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.cr.set_source_rgb(0.8, 0.8, 0.8)     
                self.cr.set_font_size(24)

                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 2)
                self.cr.show_text(str(self.song.time_signatures[c_ts]["beats"]))
                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 3.2)
                self.cr.show_text("4")

                show_ts = False

            if not draw_notes:   
                # Draws the measure number
                self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.cr.set_source_rgb(0.8, 0.2, 0.2)    
                self.cr.set_font_size(9)
                self.cr.move_to(self.c_x, self.c_y - measure_num_offset)
                self.cr.show_text(str(measure_num))                            

                # Draws the vertical lines         
                c_beat = self.song.resolution * self.m2l  
                for i in range(self.song.time_signatures[c_ts]["beats"]):  
                    if i == 0:
                        self.draw_vert_line(0.7, self.c_x + i * c_beat)
                    else:
                        self.draw_vert_line(0.9, self.c_x + i * c_beat)   

                # Draws the horizontal lines
                for i in range(5):
                    if i == 0 or i == 4:
                        self.cr.set_source_rgb(0.6, 0.6, 0.6)
                    else:
                        self.cr.set_source_rgb(0.7, 0.7, 0.7)

                    self.cr.move_to(self.c_x, self.c_y)
                    self.cr.line_to(self.c_x + measure_length * self.m2l, self.c_y) 
                    self.cr.stroke()
                    self.c_y += self.notes_offset

                self.c_y -= self.notes_offset * 5

                # Draws remaining star power phrase length from last measure
                if sp_phrase_length > 0:
                    self.cr.set_source_rgba(self.COLORS[6][0], self.COLORS[6][1], self.COLORS[6][2], 0.5)

                    if sp_phrase_length > measure_length * self.m2l:
                        self.cr.rectangle(self.c_x, self.c_y, measure_length * self.m2l, 4 * self.notes_offset)
                        sp_phrase_length -= measure_length * self.m2l               
                    else:
                        self.cr.rectangle(self.c_x, self.c_y, sp_phrase_length, 4 * self.notes_offset) 
                        sp_phrase_length = 0

                    self.cr.fill()      
                    self.cr.set_source_rgba(self.COLORS[6][0], self.COLORS[6][1], self.COLORS[6][2], 1)  

                # Draws bpms im measure
                self.cr.set_source_rgb(0, 0, 0)   
                self.cr.set_font_size(9)  
                if b < len(bpms):
                    while bpms[b]["position"] < c_length + measure_length:  
                        bpm_pos = bpms[b]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + bpm_pos

                        self.cr.move_to(x, self.c_y - measure_num_offset * 3)

                        str_bpm = "t=" + str(bpms[b]["value"])
                        self.cr.show_text(str_bpm)

                        b += 1

                        if b == len(bpms):
                            break  

                # Draws sections im measure
                self.cr.set_source_rgb(0, 0, 0)   
                if s < len(sections):
                    while sections[s]["position"] < c_length + measure_length:  
                        section_pos = sections[s]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + section_pos

                        self.cr.move_to(x, self.c_y - measure_num_offset * 5)

                        self.cr.show_text(sections[s]["name"])

                        s += 1

                        if s == len(sections):
                            break  

                # Draws star power phrases in measure 
                if sp < len(sp_phrases):
                    while sp_phrases[sp]["position"] < c_length + measure_length:  
                        sp_phrase_line_pos = sp_phrases[sp]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + sp_phrase_line_pos

                        self.cr.move_to(x, self.c_y)

                        length_pos = x + sp_phrases[sp]["length"] * self.m2l

                        measure_pos = self.MEASURE_OFFSET + (c_length + measure_length) * self.m2l - sum(self.line_lengths)
                            
                        self.cr.set_source_rgba(self.COLORS[6][0], self.COLORS[6][1], self.COLORS[6][2], 0.5)

                        if length_pos > measure_pos:             
                            self.cr.rectangle(x, self.c_y, measure_pos - x, 4 * self.notes_offset) 
                            sp_phrase_length = length_pos - measure_pos
                        else:
                            self.cr.rectangle(x, self.c_y, length_pos - x, 4 * self.notes_offset) 

                        self.cr.fill()      
                        self.cr.set_source_rgba(self.COLORS[6][0], self.COLORS[6][1], self.COLORS[6][2], 1)   


                        sp += 1

                        if sp == len(sp_phrases):
                            break  
            
            if draw_notes:
                # Draws remaining note length from last measure
                for i in range(len(note_lengths)):
                    if note_lengths[i] > 0:

                        self.cr.set_source_rgb(self.COLORS[i][0], self.COLORS[i][1], self.COLORS[i][2])
                        self.cr.move_to(self.c_x, self.c_y + i * self.notes_offset)

                        if note_lengths[i] > measure_length * self.m2l:
                            if i == 5:
                                self.cr.set_source_rgba(1, 0, 1, 0.5)
                                self.cr.rectangle(self.c_x, self.c_y, measure_length * self.m2l, 4 * self.notes_offset) 
                                self.cr.fill()      
                                self.cr.set_source_rgba(1, 0, 1, 1)   
                            else:
                                self.cr.line_to(self.c_x + measure_length * self.m2l, self.c_y + i * self.notes_offset) 
                                self.cr.stroke()

                            note_lengths[i] -= measure_length * self.m2l
                        else:
                            if i == 5:
                                self.cr.set_source_rgba(1, 0, 1, 0.5)
                                self.cr.rectangle(self.c_x, self.c_y, note_lengths[i], 4 * self.notes_offset) 
                                self.cr.fill()
                                self.cr.set_source_rgba(1, 0, 1, 1)   
                            else:
                                self.cr.line_to(self.c_x + note_lengths[i], self.c_y + i * self.notes_offset) 
                                self.cr.stroke()
                            note_lengths[i] = 0

                # Draws notes in measure     
                if n < len(self.notes): 
                    while self.notes[n]["position"] < c_length + measure_length:               
                        note_line_pos = self.notes[n]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + note_line_pos
                        y = self.c_y + (2 if self.notes[n]["number"] == 7 else self.notes[n]["number"]) * self.notes_offset 

                        self.draw_note(x, y, self.notes[n]["number"], self.chart.pos_in_phrase(self.notes[n]["position"]))

                        if self.notes[n]["length"] > 0:                    
                            self.cr.move_to(x, y)

                            length_pos = x + self.notes[n]["length"] * self.m2l

                            measure_pos = self.MEASURE_OFFSET + (c_length + measure_length) * self.m2l - sum(self.line_lengths)
                            
                            if length_pos > measure_pos:
                                if self.notes[n]["number"] == 7:
                                    self.cr.set_source_rgba(1, 0, 1, 0.5)
                                    self.cr.rectangle(x, self.c_y, measure_pos - x, 4 * self.notes_offset) 
                                    self.cr.fill()      
                                    self.cr.set_source_rgba(1, 0, 1, 1)     
                                else:
                                    self.cr.line_to(measure_pos, y) 
                                    self.cr.stroke()

                                note_lengths[5 if self.notes[n]["number"] == 7 else self.notes[n]["number"]] = \
                                    length_pos - measure_pos
                            else:
                                if self.notes[n]["number"] == 7:
                                    self.cr.set_source_rgba(1, 0, 1, 0.5)
                                    self.cr.rectangle(x, self.c_y, length_pos - x, 4 * self.notes_offset) 
                                    self.cr.fill()
                                    self.cr.set_source_rgba(1, 0, 1, 1)   
                                else:
                                    self.cr.line_to(length_pos, y)   
                                    self.cr.stroke()    

                        n += 1

                        if n == len(self.notes):
                            break            

    
            self.c_x += measure_length * self.m2l
            c_length += measure_length
            self.c_measure_length += measure_length

        if not draw_notes:
            self.draw_vert_line(0.8, self.c_x)

def main():
    app = Application()
    app.read_chart("Chart Examples/mikeorlando.chart")

    Chart_Img(app.song, app.song.charts[0])


if __name__ == "__main__":
    main()