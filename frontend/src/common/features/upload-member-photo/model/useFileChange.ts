import { IMember } from 'common/entities/member';
import { IPhoto } from '../lib';
import { Dispatch, SetStateAction, ChangeEvent } from 'react';

interface IUseFileChange {
  member: IMember | undefined | null;
  memberId: number;
  selectedFiles: IPhoto[];
  setSelectedFiles: Dispatch<SetStateAction<IPhoto[]>>;
}

export const useFileChange = ({
  member,
  memberId,
  setSelectedFiles,
}: IUseFileChange) => {
  const handleFileChange =
    (index: number) => (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0] || null;
      const isAfter = index < member?.nomination_info.after.length!;
      const name = isAfter
        ? member?.nomination_info.after[index].name
        : member?.nomination_info.before[
            index - member?.nomination_info.after.length
          ].name;
      const beforeAfter = isAfter ? 'AF' : 'BE';

      setSelectedFiles((prevSelectedFiles) =>
        prevSelectedFiles.map((selectedFile, i) =>
          i === index
            ? {
                member_nomination: memberId,
                photo: file!,
                before_after: beforeAfter,
                name: name!,
              }
            : selectedFile
        )
      );
    };

  return { handleFileChange };
};
