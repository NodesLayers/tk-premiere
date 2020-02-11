
class SessionInfo(object):

    def __init__(self, engine):
       self._engine = engine

    def __get_transitions(self, track_items, timebase):
        items = list()
        for i in track_items:
            item = dict(
                name=i.name,
                duration=i.duration.ticks/timebase,
                start=i.start.ticks/timebase,
                end=i.end.ticks/timebase,
                mediaType=i.mediaType,
                speed=i.getSpeed(),
            )
            items.append(item)
        return items

    def __get_track_items(self, track_items, timebase):
        import sgtk
        engine = sgtk.platform.current_engine()
        items = list()

        for i in track_items:
            clip_name = i.name
            # source_video = i.projectItem.name
            source_video = i.projectItem.name.replace('.mov', '.rv') if '.mov' in i.projectItem.name else i.projectItem.name
            
            # check if the clip name is a shotgun shot
            filter_ = [['code', 'is', clip_name], ['sg_sequence','is', engine.context.entity]]
            shot_exists = engine.shotgun.find('Shot', filter_, ['sg_cut_in', 'sg_cut_out', 'sg_cut_order', 'sg_cut_duration'])
            
            # get shotgun detail for the clip source video (it has to be for sure and Version Entity)
            filter_ = [['code', 'is', source_video], ['project','is', engine.context.project]]
            version = engine.shotgun.find('Version', filter_, ['code','sg_first_frame', 'sg_last_frame', 'entity'])
            
            item = dict(
                shot_exists = shot_exists,
                name=i.name,
                duration=i.duration.ticks/timebase,
                start=i.start.ticks/timebase,
                end=i.end.ticks/timebase,
                inPoint=i.inPoint.ticks/timebase,
                outPoint=i.outPoint.ticks/timebase,
                mediaType=i.mediaType,
                version=version,
                # components = i.components,
                isSelected = i.isSelected(),
                speed=i.getSpeed(),
                isAdjustmentLayer=i.isAdjustmentLayer()
            )

            items.append(item)

        return items

    def __get_tracks(self, sequence_tracks, timebase):
        tracks = list()
        for t in sequence_tracks:
            track = dict(
                id=t.id,
                name=t.name,
                mediaType=t.mediaType,
                clips=self.__get_track_items(t.clips, timebase),
                transitions=self.__get_transitions(t.transitions, timebase),
                isMuted=t.isMuted()
            )
            tracks.append(track)
        return tracks

    def __get_sequences(self, project_sequences):
        sequences = list()
        for s in project_sequences:
            timebase = s.timebase
            sequence = dict(
                sequenceID=s.sequenceID,
                name=s.name,
                inPoint=s.getInPointAsTime().ticks/timebase,
                outPoint=s.getOutPointAsTime().ticks/timebase,
                timebase=s.timebase,
                zeroPoint=s.zeroPoint/timebase,
                end=s.end/timebase,
                videoTracks=self.__get_tracks(s.videoTracks, timebase),
                audioTracks=self.__get_tracks(s.audioTracks, timebase)
            )
            sequences.append(sequence)
        return sequences

    def get_info(self):
        session_info = list()
        for p in self._engine.adobe.app.projects:
            project = dict(
                documentID=p.documentID,
                name=p.name,
                path=p.path,
                sequences=self.__get_sequences(p.sequences),
                activeSequence=p.activeSequence
            )
            session_info.append(project)
        return session_info
