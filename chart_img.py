import cairocffi as cairo
import math
from main import Application

class Chart_Img():

    WIDTH = 1024
    MEASURE_OFFSET = 40
    LINE_OFFSET = 125

    EPSILON = 0.001

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

    NOTE_COLORS = [
        [0, 1, 0], 
        [1, 0, 0], 
        [1, 1, 0],
        [0, 0.3, 1],
        [1, 0.7, 0]
    ]

    def __init__(self, song, chart):
        self.song = song
        self.chart = chart
        self.c_y = 0

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2

        self.m2l = self.line_length / (self.song.resolution * 24)

        height = self.calculate_height()

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
        (_, _, width, _, _, _) = self.cr.text_extents(chart.difficulty)
        self.cr.move_to(self.WIDTH / 2 - width / 2, self.c_y)   
        self.cr.show_text(chart.difficulty)

        est_score = "Est. Score: " + str(math.floor(self.chart.base_score(True)))
        (_, _, width, _, _, _) = self.cr.text_extents(est_score)
        self.cr.move_to(self.WIDTH - width - self.MEASURE_OFFSET / 4, self.c_y)   
        self.cr.show_text(est_score)

        self.c_y += 60

        self.draw_chart()

    def calculate_height(self):
        height = 110

        c_ts = 0
        self.c_measure_length = 0
        c_length = 0
        self.c_x = self.MEASURE_OFFSET
        

        chart_length = self.chart.notes[len(self.chart.notes) - 1]["position"] \
            + self.chart.notes[len(self.chart.notes) - 1]["length"]

        while c_length <= chart_length:
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
        self.cr.set_source_rgb(0.7, 0.7, 0.7)

        if star:
            for i in range(10):
                self.cr.line_to(self.STAR_POINTS[i][0] / 25 + x, self.STAR_POINTS[i][1] / 25 + y)
        else:
            self.cr.arc(x, y, 3, 0, 2 * math.pi)
            
        self.cr.stroke_preserve()

        self.cr.set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], self.NOTE_COLORS[color][2])

        self.cr.fill()

    def draw_vert_line(self, color, x):
        self.cr.set_source_rgb(color, color, color)
        self.cr.move_to(x, self.c_y)
        self.cr.line_to(x, self.c_y + self.notes_offset * 4) 
        self.cr.stroke()

    def draw_chart(self): 

        c_length = 0
        #c_bpm = 0
        c_ts = -1
        self.c_measure_length = 0
        self.c_x = self.MEASURE_OFFSET

        self.notes_offset = 15
        measure_num_offset = 5

        measure_num = 0
        self.line_num = 0

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2
        self.line_lengths = []

        show_ts = False

        chart_length = self.chart.notes[len(self.chart.notes) - 1]["position"] \
            + self.chart.notes[len(self.chart.notes) - 1]["length"]

        notes = self.chart.notes
        n = 0
        note_lengths = [0, 0, 0, 0, 0]
        #sp_phrases = self.chart.sp_phrases

        self.cr.set_line_width(2)

        while c_length <= chart_length:

            measure_num += 1  

            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length: 
                    show_ts = True
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"]    

            if (self.c_measure_length + measure_length) * self.m2l - self.line_length > self.EPSILON:  
                self.line_lengths.append(self.c_measure_length * self.m2l)

                self.draw_vert_line(0.7, self.c_x)

                self.c_x = self.MEASURE_OFFSET
                self.c_y += self.LINE_OFFSET
                self.c_measure_length = 0

                self.line_num += 1

            if show_ts:
                self.cr.select_font_face("Arial Black", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.cr.set_source_rgb(0.8, 0.8, 0.8)     
                self.cr.set_font_size(24)

                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 2)
                self.cr.show_text(str(self.song.time_signatures[c_ts]["beats"]))
                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 3.2)
                self.cr.show_text("4")

                show_ts = False

            self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            self.cr.set_source_rgb(0.8, 0.2, 0.2)     
            self.cr.set_font_size(9)
            self.cr.move_to(self.c_x, self.c_y - measure_num_offset)
            self.cr.show_text(str(measure_num))
            

            c_beat = self.song.resolution * self.m2l     

            # Draws the vertical lines
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
            
            # Draws remaining note length from last measure
            for i in range(len(note_lengths)):
                if note_lengths[i] > 0:

                    self.cr.set_source_rgb(self.NOTE_COLORS[i][0], self.NOTE_COLORS[i][1], self.NOTE_COLORS[i][2])
                    self.cr.move_to(self.c_x, self.c_y + i * self.notes_offset)

                    if note_lengths[i] > measure_length * self.m2l:
                        self.cr.line_to(self.c_x + measure_length * self.m2l, self.c_y + i * self.notes_offset) 
                        note_lengths[i] -= measure_length * self.m2l
                    else:
                        self.cr.line_to(self.c_x + note_lengths[i], self.c_y + i * self.notes_offset) 
                        note_lengths[i] = 0

                    self.cr.stroke()

            # Draws notes in measure
            while notes[n]["position"] < c_length + measure_length:               
                note_line_pos = notes[n]["position"] * self.m2l - sum(self.line_lengths)

                x = self.MEASURE_OFFSET + note_line_pos
                y = self.c_y + notes[n]["number"] * self.notes_offset

                self.draw_note(x, y, notes[n]["number"], False)

                if notes[n]["length"] > 0:                    
                    self.cr.move_to(x, y)

                    length_pos = x + notes[n]["length"] * self.m2l

                    measure_pos = self.MEASURE_OFFSET + (c_length + measure_length) * self.m2l - sum(self.line_lengths)
                    
                    if length_pos > measure_pos:
                        self.cr.line_to(measure_pos, y) 
                        note_lengths[notes[n]["number"]] = length_pos - measure_pos
                    else:
                        self.cr.line_to(x + notes[n]["length"] * self.m2l, y) 

                    self.cr.stroke()

                n += 1

                if n == len(notes):
                    break            

            self.c_x += measure_length * self.m2l
            c_length += measure_length
            self.c_measure_length += measure_length

        self.draw_vert_line(0.7, self.c_x)

        self.ims.write_to_png("chart.png")

def main():
    app = Application()
    app.read_chart("Chart Examples/soulless4.chart")

    Chart_Img(app.song, app.song.charts[1])


if __name__ == "__main__":
    main()