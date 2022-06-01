"""
TODO:
might start from scratch with the knowledge acquired when developing the mediainfo version

video information linemode plugin with ffprobe
"""

import json
import subprocess
import ranger.api
import ranger.core.linemode

@ranger.api.register_linemode
class MyLinemode(ranger.core.linemode.LinemodeBase):
    name = "videoinfo"

    def filetitle(self, fobj, metadata):
        return fobj.relative_path

    def infostring(self, fobj, metadata):

        def fps_output(output="medium"):
            """ prettify fps output, choose the output when calling the function:
                short: 60F
                medium(default): 60FPS
                full: 60.00FPS
            """
            if streams_dict.get("avg_frame_rate") is not None:
                if streams_dict.get("avg_frame_rate") == "0/0":
                    return ""
                fps = str(streams_dict.get("avg_frame_rate"))
                fps_list = fps.split("/")
                fps_final = ((int(fps_list[0])/int(fps_list[1])))
                if output == "short":
                    return str(round(fps_final)) + "F"
                if output == "medium":
                    return str(round(fps_final)) + "FPS"
                if output == "full":
                    return str(round(fps_final,2)) + "FPS"
            return ""

        def height_output(output="short"):
            """ to prettify and choose the output when calling the function:
                short(default): 1080P
                full: 1920x1080
            """
            if streams_dict.get("height") is not None:
                if output == "short":
                    return str(streams_dict.get("height")) + "P"
                if output == "full":
                    return "%sx%s" % (streams_dict.get("width"),streams_dict.get("height"))
            return ""

        if not fobj.is_directory:
            ffcommands = ['ffprobe','-pretty','-v','error','-show_format',
                          '-show_streams','-of','json',fobj.path]
            try:
                output = subprocess.check_output(ffcommands,
                         stderr=subprocess.STDOUT).decode("utf-8")
            except subprocess.CalledProcessError:
                return "no info"
            try:
                #some files might cause ffprobe to crash so we try to catch an exception
                json_output = json.loads(output)
                # breaking down in smaller dictionaries so it's not one big nested dictionaries
                streams_dict = dict(json_output["streams"][0])
                format_dict = dict(json_output["format"])
            except Exception:
                return "no info"
            line_output = [
                    fps_output(), # can be called with output=argument, short,medium,full ex(30F,30FPS,30.00FPS)
                    height_output(), # can be called with output=argument, short,full ex(1080P,1920x1080)
                    str(streams_dict.get("codec_name","")),
                    # removing sexagesimals since they take too much space in the line
                    str(format_dict.get("duration","")[:-7])
                    ]
            return " ".join(line_output)
        return None
