using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class LayoutSocket : MonoBehaviour
{
    private XRSocketInteractor socketInteractor;
    private string lastIcon;
    private string correctIcon;

    public string LastIcon
    { get { return lastIcon; } set { lastIcon = value; } }

    public string CorrectIcon
        { get { return correctIcon; } set { correctIcon = value; } }

    void Start()
    {
        socketInteractor = GetComponent<XRSocketInteractor>();
    }

    public void OnAttach()
    {
        IXRSelectInteractable obj = socketInteractor.GetOldestInteractableSelected();

        //print(obj.transform.name);

        if (obj.transform.GetComponent<View>() != null)
        {
            lastIcon = obj.transform.GetComponent<View>().Icon;
            print("Socket name is: " + transform.name + ". And view is: " + obj.transform.name);
        }
    }
}
