import { IMember } from 'common/entities/member';
import Link from 'next/link';
import styles from './VideoLink.module.scss';

export const VideoLink = ({ member }: { member: IMember }) => {
  return (
    <>
      {member?.url_message_video ? (
        <Link
          target="_blank"
          href={member?.url_message_video}
          className={styles.result__video_link}
        >
          Посмотреть доп. фото
        </Link>
      ) : null}
    </>
  );
};
